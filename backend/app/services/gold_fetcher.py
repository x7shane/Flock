"""
Gold Price Fetcher Service.

Fetches gold price data from yfinance (GC=F for gold in USD, INR=X for USDINR rate).
Converts to INR per gram: (gold_usd_per_oz × usdinr_rate) / 31.1035

Per data_pipeline/SKILL.md: gold_price = yf.download("GC=F") * yf.download("INR=X") / 31.1035
"""

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.gold import GoldPrice
from app.models.pipeline import PipelineRun

logger = logging.getLogger(__name__)

# Troy ounces per gram — fixed constant
TROY_OZ_PER_GRAM = 31.1035


class GoldFetcher:
    """Fetches gold price data from yfinance (GC=F × INR=X → INR/gram)."""

    RATE_LIMIT_DELAY = 1.0  # seconds between requests

    def __init__(self):
        self._last_request_time: float = 0.0

    async def _rate_limit(self) -> None:
        """Apply rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_gold_price(self, target_date: date | None = None) -> dict[str, Any] | None:
        """
        Fetch gold price in INR per gram for a given date (defaults to today).

        Uses yfinance:
          - GC=F : COMEX gold futures (USD per troy oz)
          - INR=X: USD/INR exchange rate

        Formula: price_inr_per_gram = (gold_usd × usdinr) / 31.1035

        Returns:
            Dict with gold price data, or None if fetch failed
        """
        await self._rate_limit()

        if target_date is None:
            target_date = date.today()

        # Fetch a small window so we get at least one data point
        start = target_date - timedelta(days=5)
        end = target_date + timedelta(days=1)  # yfinance end is exclusive

        try:
            loop = asyncio.get_event_loop()

            def _download() -> tuple[pd.DataFrame, pd.DataFrame]:
                gold_df = yf.download("GC=F", start=start, end=end, progress=False, auto_adjust=False)
                usd_inr_df = yf.download("INR=X", start=start, end=end, progress=False, auto_adjust=False)
                return gold_df, usd_inr_df

            gold_df, usd_inr_df = await loop.run_in_executor(None, _download)

            if gold_df.empty or usd_inr_df.empty:
                logger.warning("[GoldFetcher] Empty data returned from yfinance for date %s", target_date)
                return None

            # Flatten MultiIndex columns if present (yfinance behaviour varies by version)
            if isinstance(gold_df.columns, pd.MultiIndex):
                gold_df.columns = [col[0].lower() for col in gold_df.columns]
                usd_inr_df.columns = [col[0].lower() for col in usd_inr_df.columns]
            else:
                gold_df.columns = [c.lower() for c in gold_df.columns]
                usd_inr_df.columns = [c.lower() for c in usd_inr_df.columns]

            gold_usd = float(gold_df["close"].dropna().iloc[-1])
            usd_inr = float(usd_inr_df["close"].dropna().iloc[-1])
            price_inr_per_gram = (gold_usd * usd_inr) / TROY_OZ_PER_GRAM

            # Use the actual date of the last data point
            last_idx = gold_df.index[-1]
            actual_date = last_idx.date() if hasattr(last_idx, "date") else target_date

            logger.info(
                "[GoldFetcher] Gold: $%.2f/oz | USDINR: %.4f | Price: ₹%.2f/gram (date: %s)",
                gold_usd, usd_inr, price_inr_per_gram, actual_date,
            )

            return {
                "date": actual_date,
                "price_per_gram_inr": round(price_inr_per_gram, 2),
                "fetched_at": datetime.now(UTC),
            }

        except Exception as e:
            logger.error("[GoldFetcher] Failed to fetch gold price for %s: %s", target_date, e)
            return None

    async def fetch_gold_price_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        """
        Fetch gold prices for a full date range (backfill support).

        Downloads GC=F and INR=X for the given window and returns one
        record per trading day available in yfinance.

        Args:
            start_date: First date to fetch (inclusive)
            end_date:   Last date to fetch (inclusive)

        Returns:
            List of {date, price_per_gram_inr, fetched_at} dicts
        """
        await self._rate_limit()

        try:
            loop = asyncio.get_event_loop()

            def _download() -> tuple[pd.DataFrame, pd.DataFrame]:
                gold_df = yf.download(
                    "GC=F",
                    start=start_date,
                    end=end_date + timedelta(days=1),
                    progress=False,
                    auto_adjust=False,
                )
                usd_inr_df = yf.download(
                    "INR=X",
                    start=start_date,
                    end=end_date + timedelta(days=1),
                    progress=False,
                    auto_adjust=False,
                )
                return gold_df, usd_inr_df

            gold_df, usd_inr_df = await loop.run_in_executor(None, _download)

            if gold_df.empty or usd_inr_df.empty:
                logger.warning(
                    "[GoldFetcher] Empty range data from yfinance (%s → %s)",
                    start_date, end_date,
                )
                return []

            # Flatten MultiIndex columns
            def _flatten(df: pd.DataFrame) -> pd.DataFrame:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0].lower() for col in df.columns]
                else:
                    df.columns = [c.lower() for c in df.columns]
                return df

            gold_df = _flatten(gold_df)
            usd_inr_df = _flatten(usd_inr_df)

            # Align on common dates (both must have data for that day)
            combined = gold_df[["close"]].rename(columns={"close": "gold_usd"}).join(
                usd_inr_df[["close"]].rename(columns={"close": "usd_inr"}),
                how="inner",
            ).dropna()

            fetched_at = datetime.now(UTC)
            records = []
            for idx, row in combined.iterrows():
                actual_date = idx.date() if hasattr(idx, "date") else idx
                price_inr = (float(row["gold_usd"]) * float(row["usd_inr"])) / TROY_OZ_PER_GRAM
                records.append({
                    "date": actual_date,
                    "price_per_gram_inr": round(price_inr, 2),
                    "fetched_at": fetched_at,
                })

            logger.info(
                "[GoldFetcher] Range fetch returned %d records (%s → %s)",
                len(records), start_date, end_date,
            )
            return records

        except Exception as e:
            logger.error(
                "[GoldFetcher] Failed to fetch gold range %s→%s: %s",
                start_date, end_date, e,
            )
            return []

    async def save_gold_price(
        self,
        session: AsyncSession,
        price_data: dict[str, Any],
    ) -> bool:
        """
        Save gold price to database.

        Args:
            session: AsyncSession
            price_data: Dict with price data

        Returns:
            True if inserted, False if skipped (duplicate)
        """
        # Check if record exists for this date
        existing = await session.execute(
            select(GoldPrice).where(GoldPrice.date == price_data["date"])
        )
        if existing.scalar_one_or_none():
            logger.debug("[GoldFetcher] Gold price for %s already exists, skipping", price_data["date"])
            return False  # Skip duplicate

        # Insert new record
        price = GoldPrice(
            date=price_data["date"],
            price_per_gram_inr=price_data["price_per_gram_inr"],
            fetched_at=price_data["fetched_at"],
        )
        session.add(price)
        await session.flush()
        return True

    async def fetch_and_save(
        self,
        session: AsyncSession,
    ) -> tuple[bool, str | None]:
        """
        Fetch gold price and save to database.

        Args:
            session: AsyncSession

        Returns:
            (success, error_message)
        """
        price_data = await self.fetch_gold_price()
        if price_data is None:
            return False, "No gold price data returned from yfinance"

        inserted = await self.save_gold_price(session, price_data)
        if not inserted:
            return True, "Price already exists for today"

        return True, None


async def run_gold_price_pipeline() -> PipelineRun:
    """
    Run gold price fetch pipeline.

    Finds the last stored date in gold_prices and backfills all missing
    trading days from there to today in a single yfinance range download.

    Returns:
        PipelineRun with results
    """
    from sqlalchemy import func
    from app.models.gold import GoldPrice

    fetcher = GoldFetcher()
    run = PipelineRun(
        run_type="gold_price_fetch",
        started_at=datetime.now(UTC),
        status="running",
        tickers_total=1,
        tickers_success=0,
        tickers_failed=0,
    )

    async with async_session_factory() as session:
        session.add(run)
        await session.flush()

        today = date.today()

        # Find the last date already stored
        result = await session.execute(select(func.max(GoldPrice.date)))
        last_date: date | None = result.scalar()

        if last_date is None:
            # No history — backfill last 365 days
            start_date = today - timedelta(days=365)
        else:
            start_date = last_date + timedelta(days=1)

        if start_date > today:
            # Already up-to-date
            run.tickers_success = 1
            run.tickers_failed = 0
            run.completed_at = datetime.now(UTC)
            run.status = "completed"
            run.error_message = "Already up-to-date"
            await session.commit()
            return run

        records = await fetcher.fetch_gold_price_range(start_date, today)

        if not records:
            run.tickers_success = 0
            run.tickers_failed = 1
            run.completed_at = datetime.now(UTC)
            run.status = "failed"
            run.error_message = f"No gold data returned for {start_date} → {today}"
            await session.commit()
            return run

        inserted = 0
        for price_data in records:
            if await fetcher.save_gold_price(session, price_data):
                inserted += 1

        run.tickers_success = 1
        run.tickers_failed = 0
        run.completed_at = datetime.now(UTC)
        run.status = "completed"
        run.error_message = f"Inserted {inserted} new records ({start_date} → {today})"

        await session.commit()

    return run


async def get_gold_price_history(days: int = 30) -> list[dict[str, Any]]:
    """
    Get gold price history from database.

    Args:
        days: Number of days to retrieve

    Returns:
        List of gold price records
    """
    async with async_session_factory() as session:
        cutoff = date.today() - timedelta(days=days)
        result = await session.execute(
            select(GoldPrice)
            .where(GoldPrice.date >= cutoff)
            .order_by(GoldPrice.date.desc())
        )
        prices = result.scalars().all()

        return [
            {
                "date": p.date,
                "price_per_gram_inr": float(p.price_per_gram_inr),
            }
            for p in prices
        ]