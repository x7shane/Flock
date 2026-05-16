"""
Seed Nifty 200 Stocks.

Usage:
    python -m scripts.seed_stocks

This script populates the stocks table with the Nifty 200 universe.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.data.nifty200 import NIFTY_200


async def seed_stocks() -> None:
    """Seed the database with Nifty 200 stocks."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

    try:
        async with engine.begin() as conn:
            # Check current count
            result = await conn.execute(text("SELECT COUNT(*) FROM stocks"))
            count = result.scalar()
            print(f"Current stock count: {count}")

            if count >= len(NIFTY_200):
                print(f"Database already has {count} stocks (Nifty 200 has {len(NIFTY_200)}). Skipping seed.")
                return

            # Prepare bulk insert data
            stocks_data = [
                {
                    "ticker": stock.ticker,
                    "company_name": stock.company_name,
                    "sector": stock.sector,
                    "industry": stock.industry,
                    "is_active": True,
                }
                for stock in NIFTY_200
            ]

            # Bulk insert with ON CONFLICT to handle re-runs
            await conn.execute(
                text("""
                    INSERT INTO stocks (ticker, company_name, sector, industry, is_active, created_at, updated_at)
                    VALUES (:ticker, :company_name, :sector, :industry, :is_active, NOW(), NOW())
                    ON CONFLICT (ticker) DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        sector = EXCLUDED.sector,
                        industry = EXCLUDED.industry,
                        is_active = EXCLUDED.is_active,
                        updated_at = NOW()
                """),
                stocks_data,
            )

            # Verify count
            result = await conn.execute(text("SELECT COUNT(*) FROM stocks"))
            new_count = result.scalar()
            print(f"Successfully seeded {new_count} stocks.")

    finally:
        await engine.dispose()


def main():
    """Main entry point."""
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Nifty 200 stocks to seed: {len(NIFTY_200)}")
    print("-" * 50)

    asyncio.run(seed_stocks())


if __name__ == "__main__":
    main()
