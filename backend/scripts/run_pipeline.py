"""
Run Data Pipeline — Fetch fundamentals, prices, and compute Flock Scores.

Usage:
    python -m scripts.run_pipeline              # Full pipeline (all 218 tickers)
    python -m scripts.run_pipeline --test       # Test with 5 tickers
    python -m scripts.run_pipeline --fundamentals-only  # Only fundamentals + scoring
    python -m scripts.run_pipeline --tickers RELIANCE,TCS,INFY  # Specific tickers
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import UTC, datetime

from app.db.session import async_session_factory
from app.services.fundamentals_fetcher import FundamentalsFetcher, run_fundamentals_pipeline
from app.services.price_fetcher import run_price_fetch_pipeline
from app.services.gold_fetcher import run_gold_price_pipeline
from app.services.score_calculator import run_scoring_pipeline
from app.data.nifty200 import get_tickers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")

# Test tickers — diverse sectors for validation
TEST_TICKERS = ["RELIANCE", "TCS", "HDFCBANK", "SUNPHARMA", "TATASTEEL"]


async def run_pipeline(
    tickers: list[str],
    fundamentals_only: bool = False,
) -> None:
    """Run the full data pipeline."""
    start = time.time()
    total = len(tickers)

    print(f"\n{'='*60}")
    print(f"  FLOCK DATA PIPELINE")
    print(f"  Tickers: {total} | Started: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}\n")

    # ── Step 1: Fundamentals ──
    print(f"[1/{'2' if fundamentals_only else '4'}] Fetching fundamentals for {total} tickers...")
    print(f"    Rate limit: 1 req/sec → ETA: ~{total} seconds")
    fund_run = await run_fundamentals_pipeline(tickers)
    print(f"    ✅ Fundamentals: {fund_run.tickers_success}/{fund_run.tickers_total} succeeded | Status: {fund_run.status}")
    if fund_run.error_message:
        # Show first few errors
        errors = fund_run.error_message.split("\n")[:3]
        for e in errors:
            print(f"    ⚠️  {e}")

    if not fundamentals_only:
        # ── Step 2: Stock Prices ──
        print(f"\n[2/4] Fetching stock prices for {total} tickers (30-day window)...")
        print(f"    Rate limit: 0.5s/req → ETA: ~{total // 2} seconds")
        price_run = await run_price_fetch_pipeline(tickers, days=30)
        print(f"    ✅ Prices: {price_run.tickers_success}/{price_run.tickers_total} succeeded | Status: {price_run.status}")
        if price_run.error_message:
            errors = price_run.error_message.split("\n")[:3]
            for e in errors:
                print(f"    ⚠️  {e}")

        # ── Step 3: Gold Price ──
        print(f"\n[3/4] Fetching gold price (GC=F × INR=X)...")
        try:
            gold_run = await run_gold_price_pipeline()
            print(f"    ✅ Gold: Status: {gold_run.status}")
        except Exception as e:
            print(f"    ⚠️  Gold fetch failed: {e}")

    # ── Step 4: Scoring ──
    step_num = "2" if fundamentals_only else "4"
    total_steps = "2" if fundamentals_only else "4"
    print(f"\n[{step_num}/{total_steps}] Computing Flock Scores...")
    scoring_run = await run_scoring_pipeline()
    print(f"    ✅ Scoring: {scoring_run.tickers_success} stocks scored | Status: {scoring_run.status}")

    # ── Summary ──
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Duration: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*60}")

    # Verify DB state
    await verify_db_state()


async def verify_db_state() -> None:
    """Print DB state summary."""
    from sqlalchemy import text

    async with async_session_factory() as session:
        # Fundamentals
        result = await session.execute(text("SELECT COUNT(*) FROM fundamentals WHERE is_current = true"))
        fund_count = result.scalar()

        # Flock scores
        result = await session.execute(text("SELECT COUNT(*) FROM flock_scores WHERE is_current = true"))
        score_count = result.scalar()

        # Stock prices
        result = await session.execute(text("SELECT COUNT(DISTINCT stock_id) FROM stock_prices"))
        price_stocks = result.scalar()

        result = await session.execute(text("SELECT COUNT(*) FROM stock_prices"))
        price_rows = result.scalar()

        # Gold
        result = await session.execute(text("SELECT COUNT(*) FROM gold_prices"))
        gold_count = result.scalar()

        # Pipeline runs
        result = await session.execute(text("SELECT run_type, status, tickers_success, tickers_failed FROM pipeline_runs ORDER BY started_at DESC LIMIT 5"))
        runs = result.all()

    print(f"\n  📊 Database State:")
    print(f"     Fundamentals: {fund_count} stocks with current data")
    print(f"     Flock Scores:  {score_count} stocks scored")
    print(f"     Stock Prices:  {price_rows} rows across {price_stocks} stocks")
    print(f"     Gold Prices:   {gold_count} records")
    print(f"\n  🔄 Recent Pipeline Runs:")
    for run in runs:
        print(f"     {run[0]:25s} | {run[1]:10s} | ✅ {run[2] or 0} | ❌ {run[3] or 0}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Flock Data Pipeline")
    parser.add_argument("--test", action="store_true", help="Test with 5 tickers only")
    parser.add_argument("--fundamentals-only", action="store_true", help="Only fetch fundamentals (skip prices/gold)")
    parser.add_argument("--tickers", type=str, help="Comma-separated list of tickers")
    parser.add_argument("--verify", action="store_true", help="Only verify DB state (no fetching)")
    args = parser.parse_args()

    if args.verify:
        asyncio.run(verify_db_state())
        return

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    elif args.test:
        tickers = TEST_TICKERS
    else:
        tickers = get_tickers()

    asyncio.run(run_pipeline(tickers, fundamentals_only=args.fundamentals_only))


if __name__ == "__main__":
    main()
