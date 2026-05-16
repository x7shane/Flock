"""
Shared pytest fixtures for Flock backend tests.

Provides:
  - Override settings for test environment (avoids touching real DB)
  - Async mock session fixture for unit tests
  - Sample model factory helpers
"""

import pytest
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

from app.core.config import Settings


# ── Settings override ──────────────────────────────────────────────


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    """
    Force test-safe settings. Prevents real DB connections during unit tests.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("CORS_ORIGINS", "*")


# ── Async DB session mock ──────────────────────────────────────────


@pytest.fixture
def mock_session():
    """
    A MagicMock that mimics an AsyncSession.

    execute() returns a mock scalars-chain by default.
    flush() and commit() are AsyncMocks so they can be awaited.
    """
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()

    # Default: execute returns nothing (scalar_one_or_none → None)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    result_mock.scalars.return_value.all.return_value = []
    session.execute.return_value = result_mock

    return session


# ── Sample model factories ─────────────────────────────────────────


@pytest.fixture
def sample_stock():
    """A minimal Stock ORM object for testing."""
    from app.models.stock import Stock
    stock = Stock(
        id=1,
        ticker="RELIANCE",
        company_name="Reliance Industries Ltd",
        sector="Energy",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return stock


@pytest.fixture
def sample_fundamental(sample_stock):
    """A minimal Fundamental record for testing SCD2 logic."""
    from app.models.stock import Fundamental
    now = datetime.now(UTC)
    return Fundamental(
        id=1,
        stock_id=sample_stock.id,
        valid_from=now,
        valid_to=None,
        is_current=True,
        roe=0.15,
        pe_ratio=22.5,
        pb_ratio=2.1,
        debt_equity=0.3,
        fetched_at=now,
    )


@pytest.fixture
def sample_price_df():
    """Minimal yfinance-like DataFrame for price tests."""
    import pandas as pd
    return pd.DataFrame({
        "date": [date(2024, 1, 2), date(2024, 1, 3)],
        "open": [2400.0, 2410.0],
        "high": [2450.0, 2460.0],
        "low": [2390.0, 2400.0],
        "close": [2430.0, 2445.0],
        "adj_close": [2430.0, 2445.0],
        "volume": [1000000, 1200000],
    })
