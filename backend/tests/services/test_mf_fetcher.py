"""
Tests for MfFetcher service.

All HTTP calls to mfapi.in are mocked via httpx.
"""

import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.mf_fetcher import MfFetcher
from app.models.mutual_fund import MutualFund, MfNav


# ── Sample API response ────────────────────────────────────────────

SAMPLE_MFAPI_RESPONSE = {
    "meta": {
        "scheme_code": 119551,
        "scheme_name": "SBI Nifty 50 Index Fund - Regular Plan - Growth",
        "scheme_type": "Open Ended Schemes",
        "scheme_category": "Index Funds/ETFs",
    },
    "data": [
        {"date": "11-01-2024", "nav": "175.2345"},
        {"date": "10-01-2024", "nav": "173.8901"},
        {"date": "09-01-2024", "nav": "172.5612"},
    ],
}


def make_mock_response(json_data: dict, status_code: int = 200):
    """Build a mock httpx Response."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    return mock_resp


class TestFetchMfNav:
    """Unit tests for the single-scheme latest NAV fetch."""

    @pytest.mark.asyncio
    async def test_returns_nav_dict_on_success(self):
        """Valid API response → parsed NAV dict."""
        mock_response = make_mock_response(SAMPLE_MFAPI_RESPONSE)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.mf_fetcher.httpx.AsyncClient", return_value=mock_client):
            fetcher = MfFetcher()
            result = await fetcher.fetch_mf_nav("119551")

        assert result is not None
        assert result["scheme_code"] == "119551"
        assert result["nav"] == pytest.approx(175.2345)
        assert result["date"] == date(2024, 1, 11)

    @pytest.mark.asyncio
    async def test_returns_none_on_non_200_status(self):
        """Non-200 status → None returned."""
        mock_response = make_mock_response({}, status_code=404)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.mf_fetcher.httpx.AsyncClient", return_value=mock_client):
            fetcher = MfFetcher()
            result = await fetcher.fetch_mf_nav("999999")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_network_exception(self):
        """Network exception → None returned, not re-raised."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.mf_fetcher.httpx.AsyncClient", return_value=mock_client):
            fetcher = MfFetcher()
            result = await fetcher.fetch_mf_nav("119551")

        assert result is None


class TestFetchMfNavHistory:
    """Unit tests for the multi-day NAV history fetch."""

    @pytest.mark.asyncio
    async def test_parses_all_nav_records(self):
        """Should parse all records within the requested date range."""
        mock_response = make_mock_response(SAMPLE_MFAPI_RESPONSE)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.mf_fetcher.httpx.AsyncClient", return_value=mock_client), \
             patch("app.services.mf_fetcher.date") as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            fetcher = MfFetcher()
            results = await fetcher.fetch_mf_nav_history("119551", days=365)

        assert results is not None
        assert len(results) == 3
        assert all("nav" in r and "date" in r for r in results)

    @pytest.mark.asyncio
    async def test_skips_malformed_records(self):
        """Records with unparseable dates are gracefully skipped."""
        bad_response = {
            "meta": SAMPLE_MFAPI_RESPONSE["meta"],
            "data": [
                {"date": "11-01-2024", "nav": "175.23"},
                {"date": "bad-date", "nav": "173.00"},  # malformed
            ],
        }
        mock_response = make_mock_response(bad_response)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.mf_fetcher.httpx.AsyncClient", return_value=mock_client), \
             patch("app.services.mf_fetcher.date") as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            fetcher = MfFetcher()
            results = await fetcher.fetch_mf_nav_history("119551", days=365)

        assert results is not None
        assert len(results) == 1  # Only the valid record


class TestSaveMfNav:
    """Unit tests for saving NAV records to database."""

    @pytest.mark.asyncio
    async def test_inserts_new_nav(self, mock_session):
        """No existing NAV for this date → should insert and return True."""
        fund = MagicMock(spec=MutualFund)
        fund.id = 1

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        fetcher = MfFetcher()
        nav_data = {"date": date(2024, 1, 11), "nav": 175.2345, "scheme_code": "119551"}
        inserted = await fetcher.save_mf_nav(mock_session, fund, nav_data)

        assert inserted is True
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_duplicate_nav(self, mock_session):
        """Existing NAV for same date → skip and return False."""
        fund = MagicMock(spec=MutualFund)
        fund.id = 1
        existing_nav = MagicMock(spec=MfNav)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing_nav
        mock_session.execute.return_value = result_mock

        fetcher = MfFetcher()
        nav_data = {"date": date(2024, 1, 11), "nav": 175.2345, "scheme_code": "119551"}
        inserted = await fetcher.save_mf_nav(mock_session, fund, nav_data)

        assert inserted is False
        mock_session.add.assert_not_called()
