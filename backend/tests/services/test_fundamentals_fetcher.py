"""
Tests for FundamentalsFetcher service — specifically SCD2 version tracking logic.

All yfinance calls are mocked.
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.fundamentals_fetcher import FundamentalsFetcher
from app.models.stock import Fundamental


# ── _extract_factors tests ─────────────────────────────────────────

class TestExtractFactors:

    def test_extracts_roe(self):
        fetcher = FundamentalsFetcher()
        info = {"returnOnEquity": 0.20}
        result = fetcher._extract_factors(info)
        assert result["roe"] == pytest.approx(0.20)

    def test_none_values_stay_none(self):
        fetcher = FundamentalsFetcher()
        info = {}
        result = fetcher._extract_factors(info)
        assert result["roe"] is None
        assert result["pe_ratio"] is None
        assert result["dividend_yield"] is None

    def test_converts_percentage_roe_to_decimal(self):
        """Values > 1 are assumed to be percentages and should be divided by 100."""
        fetcher = FundamentalsFetcher()
        info = {"returnOnEquity": 20.0}  # 20% reported as float
        result = fetcher._extract_factors(info)
        assert result["roe"] == pytest.approx(0.20)

    def test_dividend_yield_percentage_converted(self):
        fetcher = FundamentalsFetcher()
        info = {"dividendYield": 2.5}  # 2.5% reported as float
        result = fetcher._extract_factors(info)
        assert result["dividend_yield"] == pytest.approx(0.025)

    def test_safe_float_handles_bad_values(self):
        fetcher = FundamentalsFetcher()
        info = {"returnOnEquity": "N/A", "trailingPE": None}
        result = fetcher._extract_factors(info)
        assert result["roe"] is None
        assert result["pe_ratio"] is None


# ── _data_changed tests ────────────────────────────────────────────

class TestDataChanged:

    def test_no_change_returns_false(self, sample_fundamental):
        fetcher = FundamentalsFetcher()
        new_data = {
            "roe": 0.15,
            "roce": None,
            "net_profit_margin": None,
            "revenue_cagr_3yr": None,
            "eps_growth_3yr": None,
            "debt_equity": 0.3,
            "current_ratio": None,
            "interest_coverage": None,
            "free_cash_flow": None,
            "pe_ratio": 22.5,
            "pb_ratio": 2.1,
            "peg_ratio": None,
            "dividend_yield": None,
            "promoter_holding_pct": None,
            "promoter_pledge_pct": None,
            "fii_dii_trend": None,
            "market_cap": None,
        }
        assert fetcher._data_changed(sample_fundamental, new_data) is False

    def test_change_detected_on_roe_update(self, sample_fundamental):
        fetcher = FundamentalsFetcher()
        new_data = {
            "roe": 0.25,  # Changed from 0.15
            "roce": None,
            "net_profit_margin": None,
            "revenue_cagr_3yr": None,
            "eps_growth_3yr": None,
            "debt_equity": 0.3,
            "current_ratio": None,
            "interest_coverage": None,
            "free_cash_flow": None,
            "pe_ratio": 22.5,
            "pb_ratio": 2.1,
            "peg_ratio": None,
            "dividend_yield": None,
            "promoter_holding_pct": None,
            "promoter_pledge_pct": None,
            "fii_dii_trend": None,
            "market_cap": None,
        }
        assert fetcher._data_changed(sample_fundamental, new_data) is True

    def test_new_value_where_none_was_registers_as_change(self, sample_fundamental):
        fetcher = FundamentalsFetcher()
        new_data = {k: None for k in ["roe", "roce", "net_profit_margin", "revenue_cagr_3yr",
                                        "eps_growth_3yr", "debt_equity", "current_ratio",
                                        "interest_coverage", "free_cash_flow", "pe_ratio",
                                        "pb_ratio", "peg_ratio", "dividend_yield",
                                        "promoter_holding_pct", "promoter_pledge_pct",
                                        "fii_dii_trend", "market_cap"]}
        new_data["roce"] = 0.18  # sample_fundamental has no roce set (it's None)
        result = fetcher._data_changed(sample_fundamental, new_data)
        assert result is True


# ── save_fundamentals_scd2 tests ───────────────────────────────────

class TestSaveFundamentalsScd2:

    @pytest.mark.asyncio
    async def test_first_record_inserted_with_is_current(self, mock_session, sample_stock):
        """If no existing fundamental, a new record with is_current=True is created."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None  # No existing record
        mock_session.execute.return_value = result_mock

        fetcher = FundamentalsFetcher()
        new_data = {
            "roe": 0.15, "roce": None, "net_profit_margin": None,
            "revenue_cagr_3yr": None, "eps_growth_3yr": None,
            "debt_equity": 0.3, "current_ratio": None, "interest_coverage": None,
            "free_cash_flow": None, "pe_ratio": 22.5, "pb_ratio": 2.1,
            "peg_ratio": None, "dividend_yield": None, "promoter_holding_pct": None,
            "promoter_pledge_pct": None, "fii_dii_trend": None, "market_cap": None,
            "fetched_at": datetime.now(UTC),
        }

        created, msg = await fetcher.save_fundamentals_scd2(mock_session, sample_stock, new_data)

        assert created is True
        assert mock_session.add.called
        # The added object should have is_current=True
        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.is_current is True

    @pytest.mark.asyncio
    async def test_unchanged_data_skips_insert(self, mock_session, sample_stock, sample_fundamental):
        """If data hasn't changed, no new record should be inserted."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sample_fundamental
        mock_session.execute.return_value = result_mock

        fetcher = FundamentalsFetcher()
        # Same values as sample_fundamental
        new_data = {
            "roe": 0.15, "roce": None, "net_profit_margin": None,
            "revenue_cagr_3yr": None, "eps_growth_3yr": None,
            "debt_equity": 0.3, "current_ratio": None, "interest_coverage": None,
            "free_cash_flow": None, "pe_ratio": 22.5, "pb_ratio": 2.1,
            "peg_ratio": None, "dividend_yield": None, "promoter_holding_pct": None,
            "promoter_pledge_pct": None, "fii_dii_trend": None, "market_cap": None,
            "fetched_at": datetime.now(UTC),
        }

        created, msg = await fetcher.save_fundamentals_scd2(mock_session, sample_stock, new_data)

        assert created is False
        assert "No changes" in msg
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_changed_data_closes_old_and_inserts_new(
        self, mock_session, sample_stock, sample_fundamental
    ):
        """When data changes, old record is closed (is_current=False) and new is inserted."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sample_fundamental
        mock_session.execute.return_value = result_mock

        fetcher = FundamentalsFetcher()
        new_data = {
            "roe": 0.25,  # Changed
            "roce": None, "net_profit_margin": None,
            "revenue_cagr_3yr": None, "eps_growth_3yr": None,
            "debt_equity": 0.3, "current_ratio": None, "interest_coverage": None,
            "free_cash_flow": None, "pe_ratio": 22.5, "pb_ratio": 2.1,
            "peg_ratio": None, "dividend_yield": None, "promoter_holding_pct": None,
            "promoter_pledge_pct": None, "fii_dii_trend": None, "market_cap": None,
            "fetched_at": datetime.now(UTC),
        }

        created, msg = await fetcher.save_fundamentals_scd2(mock_session, sample_stock, new_data)

        assert created is True
        # Old record should be closed
        assert sample_fundamental.is_current is False
        assert sample_fundamental.valid_to is not None
        # New record should be added
        assert mock_session.add.called
        new_obj = mock_session.add.call_args[0][0]
        assert new_obj.is_current is True
