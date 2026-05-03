"""
Stock Price Fetcher Service.

Fetches OHLCV data from yfinance and saves to database.
Handles rate limiting and logs failures to pipeline_runs.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session_factory
from app.models.pipeline import PipelineRun
from app.models.stock import Stock, StockPrice

if TYPE_CHECKING:
    pass

# Import yfinance (sync library, run in thread)
import yfinance as yf


class PriceFetcher:
    """Fetches stock prices from yfinance."""

    # Rate limiting: max requests per minute (yfinance has no official limit, be conservative)
    RATE_LIMIT_DELAY = 0.5  # seconds between requests

    def __init__(self):
        self._last_request_time: float = 0.0

    async def _rate_limit(self) -> None:
        """Apply rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_stock_prices(
        self,
        ticker: str,
        days: int = 30,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame | None:
        """
        Fetch OHLCV data for a single stock.

        Args:
            ticker: NSE ticker symbol (e.g., "RELIANCE")
            days: Number of days to fetch (default 30)
            start_date: Optional start date (overrides days)
            end_date: Optional end date (defaults to today)

        Returns:
            DataFrame with OHLCV data, or None if fetch failed
        """
        await self._rate_limit()

        # NSE tickers need .NS suffix for yfinance
        yf_ticker = f"{ticker}.NS"

        # Calculate date range
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days)

        try:
            # Run yfinance in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: yf.download(
                    yf_ticker,
                    start=start_date,
                    end=end_date + timedelta(days=1),  # yfinance end is exclusive
                    progress=False,
                    auto_adjust=False,
                )
            )

            if df.empty:
                return None

            # Reset index to make date a column
            df = df.reset_index()

            # Handle MultiIndex columns (yfinance >= 0.2.37 returns MultiIndex for single tickers)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower().replace(" ", "_") if isinstance(col, tuple) else str(col).lower().replace(" ", "_") for col in df.columns]
            else:
                df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

            # Normalize column names to match our schema
            column_mapping = {
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "adj_close": "adj_close",
                "adj close": "adj_close",
                "volume": "volume",
            }
            df = df.rename(columns=column_mapping)

            # Ensure date is date type
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date

            return df

        except Exception as e:
            logger.error("[PriceFetcher] Failed to fetch %s.NS: %s", ticker, e)
            return None

    async def save_prices_to_db(
        self,
        session: AsyncSession,
        stock: Stock,
        df: pd.DataFrame,
    ) -> int:
        """
        Save price data to database.

        Uses upsert logic: insert new records, skip existing (by stock_id + date).

        Args:
            session: AsyncSession
            stock: Stock model instance
            df: DataFrame with price data

        Returns:
            Number of records inserted
        """
        if df.empty:
            return 0

        inserted = 0

        for _, row in df.iterrows():
            # Check if record exists
            existing = await session.execute(
                select(StockPrice).where(
                    StockPrice.stock_id == stock.id,
                    StockPrice.date == row["date"],
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip existing

            # Insert new record
            price = StockPrice(
                stock_id=stock.id,
                date=row["date"],
                open=row.get("open"),
                high=row.get("high"),
                low=row.get("low"),
                close=row.get("close"),
                adj_close=row.get("adj_close"),
                volume=row.get("volume"),
            )
            session.add(price)
            inserted += 1

        await session.flush()
        return inserted

    async def fetch_and_save(
        self,
        session: AsyncSession,
        ticker: str,
        days: int = 30,
    ) -> tuple[bool, int, str | None]:
        """
        Fetch prices and save to database.

        Args:
            session: AsyncSession
            ticker: NSE ticker
            days: Days to fetch

        Returns:
            (success, records_inserted, error_message)
        """
        # Get stock from database
        stock = await session.execute(select(Stock).where(Stock.ticker == ticker))
        stock = stock.scalar_one_or_none()
        if not stock:
            return False, 0, f"Stock {ticker} not found in database"

        # Fetch prices
        df = await self.fetch_stock_prices(ticker, days=days)
        if df is None or df.empty:
            return False, 0, f"No price data returned for {ticker}"

        # Save to database
        inserted = await self.save_prices_to_db(session, stock, df)
        return True, inserted, None


async def run_price_fetch_pipeline(
    tickers: list[str],
    days: int = 30,
) -> PipelineRun:
    """
    Run price fetch pipeline for multiple tickers.

    Args:
        tickers: List of NSE tickers
        days: Days to fetch

    Returns:
        PipelineRun with results
    """
    fetcher = PriceFetcher()
    run = PipelineRun(
        run_type="price_fetch",
        started_at=datetime.utcnow(),
        status="running",
        tickers_total=len(tickers),
        tickers_success=0,
        tickers_failed=0,
    )

    async with async_session_factory() as session:
        session.add(run)
        await session.flush()

        success_count = 0
        failed_count = 0
        errors: list[str] = []

        for ticker in tickers:
            success, _, error = await fetcher.fetch_and_save(session, ticker, days)
            if success:
                success_count += 1
            else:
                failed_count += 1
                if error:
                    errors.append(f"{ticker}: {error}")

        run.tickers_success = success_count
        run.tickers_failed = failed_count
        run.completed_at = datetime.utcnow()

        if failed_count == 0:
            run.status = "completed"
        elif success_count == 0:
            run.status = "failed"
            run.error_message = "\n".join(errors[:10])  # First 10 errors
        else:
            run.status = "partial"
            run.error_message = "\n".join(errors[:10])

        await session.commit()

    return run


# Convenience function for single ticker
async def fetch_single_stock(ticker: str, days: int = 30) -> pd.DataFrame | None:
    """Fetch prices for a single stock (no database save)."""
    fetcher = PriceFetcher()
    return await fetcher.fetch_stock_prices(ticker, days=days)