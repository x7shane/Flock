"""
Tests for PriceFetcher service.

All yfinance calls are mocked — no real network requests made.
"""

import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.price_fetcher import PriceFetcher
from app.models.stock import Stock, StockPrice


# ── Helpers ────────────────────────────────────────────────────────

def make_yfinance_df(ticker_rows: list[dict]) -> pd.DataFrame:
    """Build a minimal DataFrame shaped like yfinance output."""
    df = pd.DataFrame(ticker_rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


# ── fetch_stock_prices tests ───────────────────────────────────────

class TestFetchStockPrices:

    @pytest.mark.asyncio
    async def test_returns_dataframe_on_success(self):
        """When yfinance returns data, fetch_stock_prices returns a non-empty DataFrame."""
        mock_df = pd.DataFrame({
            "Date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "Open": [2400.0, 2410.0],
            "High": [2450.0, 2460.0],
            "Low": [2390.0, 2400.0],
            "Close": [2430.0, 2445.0],
            "Adj Close": [2430.0, 2445.0],
            "Volume": [1_000_000, 1_200_000],
        }).set_index("Date")

        with patch("app.services.price_fetcher.yf.download", return_value=mock_df):
            fetcher = PriceFetcher()
            result = await fetcher.fetch_stock_prices("RELIANCE", days=5)

        assert result is not None
        assert not result.empty
        assert "close" in result.columns

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_dataframe(self):
        """When yfinance returns an empty DataFrame, fetch_stock_prices returns None."""
        with patch("app.services.price_fetcher.yf.download", return_value=pd.DataFrame()):
            fetcher = PriceFetcher()
            result = await fetcher.fetch_stock_prices("BADTICKER", days=5)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self):
        """When yfinance raises, fetch_stock_prices returns None without re-raising."""
        with patch("app.services.price_fetcher.yf.download", side_effect=Exception("network error")):
            fetcher = PriceFetcher()
            result = await fetcher.fetch_stock_prices("RELIANCE", days=5)

        assert result is None

    @pytest.mark.asyncio
    async def test_appends_ns_suffix(self):
        """The yfinance download must receive the .NS-suffixed ticker."""
        with patch("app.services.price_fetcher.yf.download", return_value=pd.DataFrame()) as mock_dl:
            fetcher = PriceFetcher()
            await fetcher.fetch_stock_prices("RELIANCE", days=5)
            call_args = mock_dl.call_args
            assert call_args[0][0] == "RELIANCE.NS"


# ── save_prices_to_db tests ────────────────────────────────────────

class TestSavePricesToDb:

    @pytest.mark.asyncio
    async def test_inserts_new_records(self, mock_session, sample_stock, sample_price_df):
        """New rows should be added to the session."""
        fetcher = PriceFetcher()

        # No pre-existing prices
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        inserted = await fetcher.save_prices_to_db(mock_session, sample_stock, sample_price_df)

        assert inserted == len(sample_price_df)
        assert mock_session.add.call_count == len(sample_price_df)

    @pytest.mark.asyncio
    async def test_skips_existing_records(self, mock_session, sample_stock, sample_price_df):
        """Rows that already exist in DB should be skipped."""
        fetcher = PriceFetcher()

        # All records already exist
        existing = MagicMock(spec=StockPrice)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock

        inserted = await fetcher.save_prices_to_db(mock_session, sample_stock, sample_price_df)

        assert inserted == 0
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_dataframe_returns_zero(self, mock_session, sample_stock):
        """Empty DataFrame should result in 0 insertions."""
        fetcher = PriceFetcher()
        inserted = await fetcher.save_prices_to_db(mock_session, sample_stock, pd.DataFrame())
        assert inserted == 0


# ── fetch_and_save tests ──────────────────────────────────────────

class TestFetchAndSave:

    @pytest.mark.asyncio
    async def test_fails_if_stock_not_in_db(self, mock_session):
        """If stock is not found in DB, should return (False, 0, error_message)."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        fetcher = PriceFetcher()
        success, count, error = await fetcher.fetch_and_save(mock_session, "UNKNOWN", days=5)

        assert success is False
        assert count == 0
        assert "not found" in error

    @pytest.mark.asyncio
    async def test_fails_if_no_data_returned(self, mock_session, sample_stock):
        """If yfinance returns nothing, should return (False, 0, error_message)."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sample_stock
        mock_session.execute.return_value = result_mock

        with patch("app.services.price_fetcher.yf.download", return_value=pd.DataFrame()):
            fetcher = PriceFetcher()
            success, count, error = await fetcher.fetch_and_save(mock_session, "RELIANCE", days=5)

        assert success is False
        assert "No price data" in error
