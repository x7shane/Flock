"""
Fundamentals Fetcher Service with SCD2 Logic.

Fetches fundamental factors from yfinance and saves with SCD2 tracking.
Only creates new version when data actually changes.

SCD2 Pattern:
- Each stock can have multiple fundamental records over time
- Only one record per stock has is_current=True at any time
- valid_from: when this version became active
- valid_to: when this version became inactive (NULL for current)
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session_factory
from app.models.pipeline import PipelineRun
from app.models.stock import Fundamental, Stock

if TYPE_CHECKING:
    pass

import yfinance as yf


class FundamentalsFetcher:
    """Fetches fundamental factors from yfinance with SCD2 tracking."""

    RATE_LIMIT_DELAY = 1.0  # seconds between requests (fundamentals are heavier)

    def __init__(self):
        self._last_request_time: float = 0.0

    async def _rate_limit(self) -> None:
        """Apply rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_fundamentals(self, ticker: str) -> dict[str, Any] | None:
        """
        Fetch fundamental data for a single stock.

        Args:
            ticker: NSE ticker symbol (e.g., "RELIANCE")

        Returns:
            Dict with fundamental factors, or None if fetch failed
        """
        await self._rate_limit()

        # NSE tickers need .NS suffix for yfinance
        yf_ticker = f"{ticker}.NS"

        try:
            loop = asyncio.get_event_loop()

            def fetch_data() -> dict[str, Any]:
                stock = yf.Ticker(yf_ticker)
                info = stock.info
                return info

            info = await loop.run_in_executor(None, fetch_data)

            if not info:
                return None

            # Extract and normalize the 16 factors we care about
            fundamentals = self._extract_factors(info)
            fundamentals["fetched_at"] = datetime.now(UTC)

            return fundamentals

        except Exception as e:
            logger.error("[FundamentalsFetcher] Failed to fetch %s.NS: %s", ticker, e)
            return None

    def _extract_factors(self, info: dict[str, Any]) -> dict[str, Any]:
        """
        Extract and normalize 16 fundamental factors from yfinance info.

        Handles missing data and unit conversions.
        """
        def safe_float(value: Any) -> float | None:
            """Convert to float, return None if not possible."""
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        # Profitability factors
        roe = safe_float(info.get("returnOnEquity"))
        if roe is not None and roe > 1:  # Likely a percentage, convert to decimal
            roe = roe / 100

        roce = safe_float(info.get("operatingMargins"))
        if roce is not None and roce > 1:
            roce = roce / 100

        net_profit_margin = safe_float(info.get("profitMargins"))
        if net_profit_margin is not None and net_profit_margin > 1:
            net_profit_margin = net_profit_margin / 100

        # Growth factors
        revenue_growth = safe_float(info.get("revenueGrowth"))
        if revenue_growth is not None and revenue_growth > 1:
            revenue_growth = revenue_growth / 100

        eps_growth = safe_float(info.get("earningsGrowth"))
        if eps_growth is not None and eps_growth > 1:
            eps_growth = eps_growth / 100

        # Health factors
        debt_equity = safe_float(info.get("debtToEquity"))
        current_ratio = safe_float(info.get("currentRatio"))
        interest_coverage = safe_float(info.get("interestCoverage"))

        # Free Cash Flow (in absolute value, convert to INR if needed)
        fcf = safe_float(info.get("freeCashflow"))

        # Valuation factors
        pe_ratio = safe_float(info.get("trailingPE"))
        pb_ratio = safe_float(info.get("priceToBook"))
        peg_ratio = safe_float(info.get("pegRatio"))
        dividend_yield = safe_float(info.get("dividendYield"))
        if dividend_yield is not None and dividend_yield > 1:
            dividend_yield = dividend_yield / 100

        # Quality factors
        promoter_holding = safe_float(info.get("heldPercentInsiders"))
        if promoter_holding is not None and promoter_holding > 1:
            promoter_holding = promoter_holding / 100

        promoter_pledge = None  # Not available in yfinance, would need alternate source

        fii_dii_trend = None  # Would need alternate source (NSE/BSE data)

        # Market cap
        market_cap = safe_float(info.get("marketCap"))

        return {
            # Profitability
            "roe": roe,
            "roce": roce,
            "net_profit_margin": net_profit_margin,
            # Growth
            "revenue_cagr_3yr": revenue_growth,  # Approximation
            "eps_growth_3yr": eps_growth,
            # Health
            "debt_equity": debt_equity,
            "current_ratio": current_ratio,
            "interest_coverage": interest_coverage,
            "free_cash_flow": fcf,
            # Valuation
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "peg_ratio": peg_ratio,
            "dividend_yield": dividend_yield,
            # Quality
            "promoter_holding_pct": promoter_holding,
            "promoter_pledge_pct": promoter_pledge,
            "fii_dii_trend": fii_dii_trend,
            # Metadata
            "market_cap": market_cap,
        }

    def _data_changed(
        self,
        existing: Fundamental,
        new_data: dict[str, Any],
    ) -> bool:
        """
        Check if fundamental data has actually changed.

        Compares all 16 factors to detect meaningful changes.
        Ignores minor floating point differences.
        """
        # Factors to compare (excluding metadata)
        factor_keys = [
            "roe", "roce", "net_profit_margin",
            "revenue_cagr_3yr", "eps_growth_3yr",
            "debt_equity", "current_ratio", "interest_coverage", "free_cash_flow",
            "pe_ratio", "pb_ratio", "peg_ratio", "dividend_yield",
            "promoter_holding_pct", "promoter_pledge_pct", "fii_dii_trend",
            "market_cap",
        ]

        for key in factor_keys:
            old_val = getattr(existing, key, None)
            new_val = new_data.get(key)

            # Both None = no change
            if old_val is None and new_val is None:
                continue

            # One None, one not = change
            if old_val is None or new_val is None:
                return True

            # Both have values, compare with tolerance
            if abs(float(old_val) - float(new_val)) > 0.0001:
                return True

        return False

    async def save_fundamentals_scd2(
        self,
        session: AsyncSession,
        stock: Stock,
        data: dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Save fundamentals with SCD2 logic.

        1. Get current fundamental record (is_current=True)
        2. Compare with new data
        3. If changed:
           a. Close current record (set valid_to, is_current=False)
           b. Insert new record (valid_from=now, valid_to=NULL, is_current=True)
        4. If no change: skip (avoid duplicate history)

        Args:
            session: AsyncSession
            stock: Stock model instance
            data: Dict with fundamental factors

        Returns:
            (created_new_version, message)
        """
        now = datetime.now(UTC)

        # Get current fundamental record
        current = await session.execute(
            select(Fundamental).where(
                Fundamental.stock_id == stock.id,
                Fundamental.is_current == True,
            )
        )
        current = current.scalar_one_or_none()

        if current:
            # Check if data changed
            if not self._data_changed(current, data):
                return False, "No changes detected, skipped"

            # Close current record
            current.valid_to = now
            current.is_current = False

        # Insert new record
        new_fundamental = Fundamental(
            stock_id=stock.id,
            valid_from=now,
            valid_to=None,
            is_current=True,
            **data,
        )
        session.add(new_fundamental)

        await session.flush()
        if current:
            logger.info("[FundamentalsFetcher] %s: closed previous version, created new SCD2 record", stock.ticker)
        else:
            logger.info("[FundamentalsFetcher] %s: first fundamental record created", stock.ticker)
        return True, f"Created new version at {now}"

    async def fetch_and_save(
        self,
        session: AsyncSession,
        ticker: str,
    ) -> tuple[bool, str | None]:
        """
        Fetch fundamentals and save with SCD2.

        Args:
            session: AsyncSession
            ticker: NSE ticker

        Returns:
            (success, error_message)
        """
        # Get stock from database
        stock = await session.execute(select(Stock).where(Stock.ticker == ticker))
        stock = stock.scalar_one_or_none()
        if not stock:
            return False, f"Stock {ticker} not found in database"

        # Fetch fundamentals
        data = await self.fetch_fundamentals(ticker)
        if data is None:
            return False, f"No fundamental data returned for {ticker}"

        # Save with SCD2
        _, message = await self.save_fundamentals_scd2(session, stock, data)
        return True, message


async def run_fundamentals_pipeline(
    tickers: list[str],
) -> PipelineRun:
    """
    Run fundamentals fetch pipeline for multiple tickers.

    Each ticker gets its own short-lived session to avoid Neon connection
    idle timeouts during the ~3-4 minute fetch window.

    Args:
        tickers: List of NSE tickers

    Returns:
        PipelineRun with results
    """
    fetcher = FundamentalsFetcher()
    run = PipelineRun(
        run_type="fundamentals_fetch",
        started_at=datetime.now(UTC),
        status="running",
        tickers_total=len(tickers),
        tickers_success=0,
        tickers_failed=0,
    )

    # Persist the initial run record
    async with async_session_factory() as init_session:
        init_session.add(run)
        await init_session.commit()
        await init_session.refresh(run)
        run_id = run.id

    success_count = 0
    failed_count = 0
    errors: list[str] = []

    for ticker in tickers:
        # Fresh session per ticker — keeps connections short-lived for Neon
        async with async_session_factory() as session:
            success, message = await fetcher.fetch_and_save(session, ticker)
            await session.commit()

        if success:
            success_count += 1
        else:
            failed_count += 1
            if message:
                errors.append(f"{ticker}: {message}")

    # Update the run record with final counts
    async with async_session_factory() as final_session:
        result = await final_session.execute(
            select(PipelineRun).where(PipelineRun.id == run_id)
        )
        run = result.scalar_one()
        run.tickers_success = success_count
        run.tickers_failed = failed_count
        run.completed_at = datetime.now(UTC)

        if failed_count == 0:
            run.status = "completed"
        elif success_count == 0:
            run.status = "failed"
            run.error_message = "\n".join(errors[:10])
        else:
            run.status = "partial"
            run.error_message = "\n".join(errors[:10])

        await final_session.commit()

    return run


# Convenience function for single ticker
async def fetch_single_fundamentals(ticker: str) -> dict[str, Any] | None:
    """Fetch fundamentals for a single stock (no database save)."""
    fetcher = FundamentalsFetcher()
    return await fetcher.fetch_fundamentals(ticker)