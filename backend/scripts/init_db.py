"""
Database Initialization Script.

Usage:
    python -m scripts.init_db [--seed]

Options:
    --seed    Also seed the database with Nifty 200 stocks
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.stock import Stock


async def init_database(seed_stocks: bool = False) -> None:
    """
    Initialize the database.

    1. Run Alembic migrations
    2. Optionally seed with Nifty 200 stocks
    """
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

    try:
        # Test connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("Database connection successful.")

        if seed_stocks:
            await seed_nifty_200(engine)
        else:
            print("Database is ready. Use --seed to populate Nifty 200 stocks.")

    finally:
        await engine.dispose()

    print("Database initialization complete.")


async def seed_nifty_200(engine) -> None:
    """Seed the database with Nifty 200 stocks."""
    from app.data.nifty200 import NIFTY_200

    print(f"Seeding {len(NIFTY_200)} Nifty 200 stocks...")

    async with engine.begin() as conn:
        # Check if stocks already exist
        result = await conn.execute(text("SELECT COUNT(*) FROM stocks"))
        count = result.scalar()

        if count > 0:
            print(f"Database already has {count} stocks. Skipping seed.")
            return

        # Bulk insert stocks
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

        await conn.execute(
            text("""
                INSERT INTO stocks (ticker, company_name, sector, industry, is_active, created_at, updated_at)
                VALUES (:ticker, :company_name, :sector, :industry, :is_active, NOW(), NOW())
                ON CONFLICT (ticker) DO NOTHING
            """),
            stocks_data,
        )

        print(f"Successfully seeded {len(stocks_data)} stocks.")


def main():
    """Main entry point."""
    seed = "--seed" in sys.argv

    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Seed stocks: {seed}")
    print("-" * 50)

    asyncio.run(init_database(seed_stocks=seed))


if __name__ == "__main__":
    main()
