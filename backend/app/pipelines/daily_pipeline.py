"""
Daily Pipeline Orchestration.

Orchestrates all daily data fetches:
- Stock prices (yfinance)
- Fundamentals (yfinance with SCD2)
- MF NAV (mfapi.in)
- Gold price (external API)
"""

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.data.nifty200 import NIFTY_200, get_tickers
from app.db.session import async_session_factory
from app.models.mutual_fund import MutualFund
from app.models.pipeline import PipelineRun
from app.models.stock import Stock
from app.services.fundamentals_fetcher import FundamentalsFetcher
from app.services.gold_fetcher import GoldFetcher
from app.services.mf_fetcher import MfFetcher
from app.services.price_fetcher import PriceFetcher

if TYPE_CHECKING:
    pass


class DailyPipeline:
    """
    Orchestrates daily data fetch pipeline.

    Usage:
        pipeline = DailyPipeline()
        results = await pipeline.run()

    Results include:
        - price_run: PipelineRun for stock prices
        - fundamentals_run: PipelineRun for fundamentals
        - mf_nav_run: PipelineRun for MF NAV
        - gold_run: PipelineRun for gold price
    """

    def __init__(self, tickers: list[str] | None = None):
        """
        Initialize pipeline.

        Args:
            tickers: Optional list of tickers. If None, uses Nifty 200.
        """
        self.tickers = tickers or get_tickers()
        self.price_fetcher = PriceFetcher()
        self.fundamentals_fetcher = FundamentalsFetcher()
        self.mf_fetcher = MfFetcher()
        self.gold_fetcher = GoldFetcher()

    async def ensure_stocks_exist(self, session: AsyncSession) -> int:
        """
        Ensure all tickers exist in stocks table.

        Creates missing stocks with basic info from NIFTY_200 data.

        Args:
            session: AsyncSession

        Returns:
            Number of stocks created
        """
        created = 0
        ticker_to_info = {s.ticker: s for s in NIFTY_200}

        for ticker in self.tickers:
            existing = await session.execute(
                select(Stock).where(Stock.ticker == ticker)
            )
            if existing.scalar_one_or_none():
                continue

            # Create new stock
            info = ticker_to_info.get(ticker)
            stock = Stock(
                ticker=ticker,
                company_name=info.company_name if info else ticker,
                sector=info.sector if info else None,
                industry=info.industry if info else None,
                is_active=True,
            )
            session.add(stock)
            created += 1

        await session.flush()
        return created

    async def run_price_pipeline(self) -> PipelineRun:
        """Run stock price fetch pipeline."""
        return await self.price_fetcher.run_price_pipeline(self.tickers, days=30)

    async def run_fundamentals_pipeline(self) -> PipelineRun:
        """Run fundamentals fetch pipeline with SCD2."""
        return await self.fundamentals_fetcher.run_fundamentals_pipeline(self.tickers)

    async def run_mf_nav_pipeline(self) -> PipelineRun:
        """Run MF NAV fetch pipeline."""
        # Get all scheme codes from database
        async with async_session_factory() as session:
            result = await session.execute(select(MutualFund.scheme_code))
            scheme_codes = [row[0] for row in result.all()]

        if not scheme_codes:
            # Return empty result if no MFs configured
            run = PipelineRun(
                run_type="mf_nav_fetch",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                status="completed",
                tickers_total=0,
                tickers_success=0,
                tickers_failed=0,
            )
            return run

        return await self.mf_fetcher.run_mf_nav_pipeline(scheme_codes, days=30)

    async def run_gold_pipeline(self) -> PipelineRun:
        """Run gold price fetch pipeline."""
        return await self.gold_fetcher.run_gold_price_pipeline()

    async def run(self) -> dict[str, PipelineRun]:
        """
        Run all daily pipelines concurrently.

        Returns:
            Dict with PipelineRun for each pipeline type
        """
        # First, ensure stocks exist
        async with async_session_factory() as session:
            created = await self.ensure_stocks_exist(session)
            await session.commit()

        # Run all pipelines concurrently
        results = await asyncio.gather(
            self.run_price_pipeline(),
            self.run_fundamentals_pipeline(),
            self.run_mf_nav_pipeline(),
            self.run_gold_pipeline(),
            return_exceptions=True,
        )

        # Process results
        pipeline_names = ["price_run", "fundamentals_run", "mf_nav_run", "gold_run"]
        output = {}

        for name, result in zip(pipeline_names, results):
            if isinstance(result, Exception):
                # Create failed run for exception
                run = PipelineRun(
                    run_type=name.replace("_run", "_fetch"),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    status="failed",
                    error_message=str(result),
                )
            else:
                run = result
            output[name] = run

        return output


async def run_daily_pipeline(tickers: list[str] | None = None) -> dict[str, PipelineRun]:
    """
    Convenience function to run daily pipeline.

    Args:
        tickers: Optional list of tickers. If None, uses Nifty 200.

    Returns:
        Dict with PipelineRun for each pipeline type
    """
    pipeline = DailyPipeline(tickers)
    return await pipeline.run()


class IncrementalPipeline:
    """
    Pipeline for incremental updates (less frequent full refresh).

    - Daily: Stock prices, MF NAV, Gold price
    - Weekly: Fundamentals (SCD2 handles changes)
    """

    def __init__(self, tickers: list[str] | None = None):
        self.tickers = tickers or get_tickers()
        self.daily_pipeline = DailyPipeline(self.tickers)

    async def run_daily(self) -> dict[str, PipelineRun]:
        """Run daily pipelines (prices, NAV, gold)."""
        results = {}

        # Stock prices
        results["price_run"] = await self.daily_pipeline.run_price_pipeline()

        # MF NAV
        results["mf_nav_run"] = await self.daily_pipeline.run_mf_nav_pipeline()

        # Gold price
        results["gold_run"] = await self.daily_pipeline.run_gold_pipeline()

        return results

    async def run_weekly(self) -> dict[str, PipelineRun]:
        """Run weekly pipeline (full refresh including fundamentals)."""
        return await self.daily_pipeline.run()


# Scheduler configuration (for APScheduler integration)
SCHEDULE_CONFIG = {
    "daily_prices": {
        "func": run_daily_pipeline,
        "trigger": "cron",
        "hour": 6,  # 6 AM IST (after market close)
        "minute": 0,
    },
    "weekly_fundamentals": {
        "func": IncrementalPipeline().run_weekly,
        "trigger": "cron",
        "day_of_week": "sat",  # Saturday
        "hour": 8,
        "minute": 0,
    },
}