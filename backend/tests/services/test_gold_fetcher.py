"""
Tests for GoldFetcher service.

All yfinance calls are mocked — no real network requests made.
"""

import pytest
import pandas as pd
from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

from app.services.gold_fetcher import GoldFetcher, TROY_OZ_PER_GRAM


def make_gold_df(close_price: float) -> pd.DataFrame:
    """Build a minimal yfinance-like DataFrame for gold tests."""
    return pd.DataFrame(
        {"Close": [close_price]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-03")]),
    )


class TestFetchGoldPrice:

    @pytest.mark.asyncio
    async def test_returns_price_dict_on_success(self):
        """When both GC=F and INR=X return data, should compute price correctly."""
        gold_df = make_gold_df(2050.0)   # USD per troy oz
        usd_inr_df = make_gold_df(83.5)  # USDINR rate

        expected_price = round((2050.0 * 83.5) / TROY_OZ_PER_GRAM, 2)

        with patch("app.services.gold_fetcher.yf.download", side_effect=[gold_df, usd_inr_df]):
            fetcher = GoldFetcher()
            result = await fetcher.fetch_gold_price(target_date=date(2024, 1, 3))

        assert result is not None
        assert result["price_per_gram_inr"] == pytest.approx(expected_price, abs=1.0)
        assert "date" in result
        assert "fetched_at" in result

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_data(self):
        """If either feed returns empty DataFrame, should return None."""
        with patch("app.services.gold_fetcher.yf.download", return_value=pd.DataFrame()):
            fetcher = GoldFetcher()
            result = await fetcher.fetch_gold_price()

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self):
        """If yfinance throws, should return None without re-raising."""
        with patch("app.services.gold_fetcher.yf.download", side_effect=Exception("timeout")):
            fetcher = GoldFetcher()
            result = await fetcher.fetch_gold_price()

        assert result is None

    def test_troy_oz_constant_is_correct(self):
        """Sanity check — 1 troy oz = 31.1035 grams."""
        assert TROY_OZ_PER_GRAM == pytest.approx(31.1035)


class TestSaveGoldPrice:

    @pytest.mark.asyncio
    async def test_inserts_new_price(self, mock_session):
        """No existing record → should insert and return True."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        fetcher = GoldFetcher()
        price_data = {
            "date": date(2024, 1, 3),
            "price_per_gram_inr": 5523.45,
            "fetched_at": datetime.now(UTC),
        }
        inserted = await fetcher.save_gold_price(mock_session, price_data)

        assert inserted is True
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_duplicate_price(self, mock_session):
        """Existing record for same date → should skip and return False."""
        from app.models.gold import GoldPrice
        existing = MagicMock(spec=GoldPrice)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock

        fetcher = GoldFetcher()
        price_data = {
            "date": date(2024, 1, 3),
            "price_per_gram_inr": 5523.45,
            "fetched_at": datetime.now(UTC),
        }
        inserted = await fetcher.save_gold_price(mock_session, price_data)

        assert inserted is False
        mock_session.add.assert_not_called()
