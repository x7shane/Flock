"""
Tests for Historical Stress Test Engine.

Uses synthetic price data that mimics crisis-period behavior.
"""

import numpy as np
import pandas as pd
import pytest

from app.services.stress_test import (
    CRISIS_PERIODS,
    get_available_crises,
    run_stress_test,
    run_all_stress_tests,
)


# ── Test Fixtures ───────────────────────────────────────────────────


def _make_crisis_prices(
    tickers: list[str],
    start: str = "2020-01-01",
    end: str = "2020-06-30",
    crash_pct: float = -0.30,
) -> pd.DataFrame:
    """
    Generate synthetic prices that simulate a crash and partial recovery.

    The price drops `crash_pct` over the first half, then recovers
    partially over the second half.
    """
    dates = pd.bdate_range(start, end)
    n = len(dates)
    mid = n // 2

    prices = {}
    for ticker in tickers:
        # Initial price at 100
        p = np.ones(n) * 100.0
        # Crash phase: gradual decline
        for i in range(1, mid):
            daily_drop = crash_pct / mid
            p[i] = p[i - 1] * (1 + daily_drop)
        # Recovery phase: partial bounce
        recovery_pct = abs(crash_pct) * 0.6  # Recover 60% of the drop
        for i in range(mid, n):
            daily_gain = recovery_pct / (n - mid)
            p[i] = p[i - 1] * (1 + daily_gain)
        prices[ticker] = p

    return pd.DataFrame(prices, index=dates)


# ── Crisis Database Tests ───────────────────────────────────────────


class TestCrisisPeriods:
    """Tests for the crisis period database."""

    def test_has_five_crises(self):
        """Should have 5 pre-defined crisis periods."""
        assert len(CRISIS_PERIODS) == 5

    def test_all_crises_have_required_fields(self):
        """Each crisis must have name, start, end, drawdown, description."""
        required = ["name", "start", "end", "nifty_50_drawdown_pct", "description"]
        for crisis_id, crisis in CRISIS_PERIODS.items():
            for field in required:
                assert field in crisis, f"{crisis_id} missing '{field}'"

    def test_get_available_crises_returns_list(self):
        """UI helper should return list of dicts."""
        crises = get_available_crises()
        assert len(crises) == 5
        assert all("id" in c and "name" in c for c in crises)


# ── Stress Test Logic Tests ─────────────────────────────────────────


class TestRunStressTest:
    """Tests for the core stress test logic."""

    def test_returns_drawdown_result(self):
        """Should return a dict with drawdown stats."""
        prices = _make_crisis_prices(
            ["A.NS", "B.NS"],
            start="2020-02-01", end="2020-06-30",
            crash_pct=-0.35,
        )
        result = run_stress_test(
            portfolio_tickers=["A.NS", "B.NS"],
            portfolio_weights=np.array([0.6, 0.4]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )

        assert "portfolio_max_drawdown_pct" in result
        assert "max_drawdown_date" in result
        assert "worst_single_day_pct" in result
        assert "recovery_days" in result

    def test_drawdown_is_negative(self):
        """Max drawdown should be a negative percentage."""
        prices = _make_crisis_prices(
            ["A.NS"], start="2020-02-01", end="2020-06-30", crash_pct=-0.30
        )
        result = run_stress_test(
            portfolio_tickers=["A.NS"],
            portfolio_weights=np.array([1.0]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )
        assert result["portfolio_max_drawdown_pct"] < 0

    def test_loss_at_trough_is_positive(self):
        """Loss at trough should be positive INR amount."""
        prices = _make_crisis_prices(
            ["A.NS"], start="2020-02-01", end="2020-06-30", crash_pct=-0.25
        )
        result = run_stress_test(
            portfolio_tickers=["A.NS"],
            portfolio_weights=np.array([1.0]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )
        assert result["loss_at_trough_inr"] > 0

    def test_handles_missing_tickers(self):
        """Should analyze available tickers and report missing ones."""
        prices = _make_crisis_prices(
            ["A.NS"], start="2020-02-01", end="2020-06-30",
        )
        result = run_stress_test(
            portfolio_tickers=["A.NS", "MISSING.NS"],
            portfolio_weights=np.array([0.6, 0.4]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )
        assert "A.NS" in result["tickers_analyzed"]
        assert "MISSING.NS" in result["tickers_missing"]

    def test_error_when_no_tickers_available(self):
        """Should return error dict when no ticker data exists."""
        prices = pd.DataFrame({"X.NS": [100, 101]})
        result = run_stress_test(
            portfolio_tickers=["A.NS"],
            portfolio_weights=np.array([1.0]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )
        assert "error" in result

    def test_rejects_invalid_crisis_id(self):
        """Should raise ValueError for unknown crisis."""
        prices = _make_crisis_prices(["A.NS"])
        with pytest.raises(ValueError, match="Unknown crisis"):
            run_stress_test(
                portfolio_tickers=["A.NS"],
                portfolio_weights=np.array([1.0]),
                historical_prices=prices,
                crisis_id="fake_crisis",
                initial_capital=1_000_000,
            )

    def test_rejects_negative_capital(self):
        """Should reject negative initial capital."""
        prices = _make_crisis_prices(["A.NS"])
        with pytest.raises(ValueError, match="positive"):
            run_stress_test(
                portfolio_tickers=["A.NS"],
                portfolio_weights=np.array([1.0]),
                historical_prices=prices,
                crisis_id="2020_covid_crash",
                initial_capital=-100,
            )

    def test_rejects_weight_mismatch(self):
        """Should reject if ticker/weight counts don't match."""
        prices = _make_crisis_prices(["A.NS"])
        with pytest.raises(ValueError, match="mismatch"):
            run_stress_test(
                portfolio_tickers=["A.NS"],
                portfolio_weights=np.array([0.5, 0.5]),
                historical_prices=prices,
                crisis_id="2020_covid_crash",
                initial_capital=1_000_000,
            )

    def test_includes_nifty_comparison(self):
        """Result should include Nifty 50 drawdown for comparison."""
        prices = _make_crisis_prices(
            ["A.NS"], start="2020-02-01", end="2020-06-30",
        )
        result = run_stress_test(
            portfolio_tickers=["A.NS"],
            portfolio_weights=np.array([1.0]),
            historical_prices=prices,
            crisis_id="2020_covid_crash",
            initial_capital=1_000_000,
        )
        assert result["nifty_50_drawdown_pct"] == -38.4


# ── Run All Tests ───────────────────────────────────────────────────


class TestRunAllStressTests:
    """Tests for batch stress test execution."""

    def test_returns_one_result_per_crisis(self):
        """Should return exactly 5 results (one per crisis)."""
        # Create prices spanning all crisis periods
        dates = pd.bdate_range("2007-01-01", "2023-01-01")
        prices = pd.DataFrame(
            {"A.NS": np.linspace(100, 200, len(dates))},
            index=dates,
        )

        results = run_all_stress_tests(
            portfolio_tickers=["A.NS"],
            portfolio_weights=np.array([1.0]),
            historical_prices=prices,
            initial_capital=1_000_000,
        )
        assert len(results) == 5
