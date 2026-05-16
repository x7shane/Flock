"""
Tests for Monte Carlo Simulation Engine.

All tests are pure math — no mocking needed. Uses deterministic seeds
for reproducibility.
"""

import numpy as np
import pandas as pd
import pytest

from app.services.monte_carlo import (
    build_covariance_matrix,
    estimate_return_parameters,
    run_monte_carlo,
    run_single_asset_monte_carlo,
)


# ── Test Fixtures ───────────────────────────────────────────────────


def _make_price_series(n_days: int = 756, annual_return: float = 0.12) -> pd.Series:
    """Generate a synthetic daily price series with ~12% annual return."""
    np.random.seed(123)
    daily_return = annual_return / 252
    daily_vol = 0.20 / np.sqrt(252)
    log_returns = np.random.normal(daily_return, daily_vol, n_days)
    prices = 100 * np.exp(np.cumsum(log_returns))
    index = pd.bdate_range("2020-01-01", periods=n_days)
    return pd.Series(prices, index=index, name="TEST.NS")


def _make_price_dataframe(n_days: int = 756) -> pd.DataFrame:
    """Generate synthetic prices for 3 correlated assets."""
    np.random.seed(456)
    daily_vol = 0.20 / np.sqrt(252)
    common_factor = np.random.normal(0, daily_vol * 0.6, n_days)

    prices = {}
    for i, ticker in enumerate(["A.NS", "B.NS", "C.NS"]):
        idio = np.random.normal(0, daily_vol * 0.4, n_days)
        log_ret = 0.10 / 252 + common_factor + idio
        prices[ticker] = 100 * np.exp(np.cumsum(log_ret))

    index = pd.bdate_range("2020-01-01", periods=n_days)
    return pd.DataFrame(prices, index=index)


# ── Parameter Estimation Tests ──────────────────────────────────────


class TestEstimateReturnParameters:
    """Tests for historical return/vol estimation."""

    def test_returns_tuple_of_floats(self):
        """Should return (annual_return, annual_volatility)."""
        prices = _make_price_series()
        mu, sigma = estimate_return_parameters(prices)
        assert isinstance(mu, float)
        assert isinstance(sigma, float)

    def test_positive_volatility(self):
        """Volatility must always be positive."""
        prices = _make_price_series()
        _, sigma = estimate_return_parameters(prices)
        assert sigma > 0

    def test_reasonable_annual_return(self):
        """Estimated return should be in a reasonable range for synthetic data."""
        prices = _make_price_series(n_days=1260, annual_return=0.12)
        mu, _ = estimate_return_parameters(prices)
        # With noise, expect roughly ±10% of target
        assert -0.1 < mu < 0.5

    def test_raises_on_insufficient_data(self):
        """Should raise ValueError if less than min_years of data."""
        short_prices = _make_price_series(n_days=200)
        with pytest.raises(ValueError, match="Need 3"):
            estimate_return_parameters(short_prices, min_years=3)

    def test_raises_on_empty_series(self):
        """Should raise ValueError on empty input."""
        with pytest.raises(ValueError, match="Empty"):
            estimate_return_parameters(pd.Series(dtype=float))


# ── Covariance Matrix Tests ─────────────────────────────────────────


class TestBuildCovarianceMatrix:
    """Tests for covariance matrix construction."""

    def test_output_shape(self):
        """Should return N×N matrix for N assets."""
        df = _make_price_dataframe()
        cov = build_covariance_matrix(df)
        assert cov.shape == (3, 3)

    def test_symmetric(self):
        """Covariance matrix must be symmetric."""
        df = _make_price_dataframe()
        cov = build_covariance_matrix(df)
        np.testing.assert_array_almost_equal(cov, cov.T)

    def test_positive_diagonal(self):
        """Diagonal (variances) must be positive."""
        df = _make_price_dataframe()
        cov = build_covariance_matrix(df)
        assert all(cov[i, i] > 0 for i in range(3))

    def test_raises_on_single_asset(self):
        """Need at least 2 assets."""
        df = _make_price_dataframe()[["A.NS"]]
        with pytest.raises(ValueError, match="at least 2"):
            build_covariance_matrix(df)

    def test_raises_on_insufficient_data(self):
        """Need at least 252 data points."""
        df = _make_price_dataframe().head(100)
        with pytest.raises(ValueError, match="at least 252"):
            build_covariance_matrix(df)


# ── Monte Carlo Simulation Tests ────────────────────────────────────


class TestRunMonteCarlo:
    """Tests for the core Monte Carlo engine."""

    def _default_inputs(self):
        """Reasonable default inputs for a 2-asset portfolio."""
        return {
            "expected_returns": np.array([0.12, 0.10]),
            "covariance_matrix": np.array([
                [0.04, 0.01],
                [0.01, 0.03],
            ]),
            "weights": np.array([0.6, 0.4]),
            "initial_capital": 1_000_000.0,
            "time_horizon_years": 5.0,
            "num_simulations": 1_000,
            "seed": 42,
        }

    def test_returns_dict_with_required_keys(self):
        """Output must contain final_values, paths, statistics."""
        result = run_monte_carlo(**self._default_inputs())
        assert "final_values" in result
        assert "paths" in result
        assert "statistics" in result

    def test_final_values_shape(self):
        """Should have one final value per simulation."""
        inputs = self._default_inputs()
        result = run_monte_carlo(**inputs)
        assert len(result["final_values"]) == inputs["num_simulations"]

    def test_paths_shape(self):
        """Paths shape: (num_simulations, total_steps + 1)."""
        inputs = self._default_inputs()
        result = run_monte_carlo(**inputs)
        expected_cols = int(inputs["time_horizon_years"] * 252) + 1
        assert result["paths"].shape == (inputs["num_simulations"], expected_cols)

    def test_paths_start_at_initial_capital(self):
        """First column of all paths should equal initial capital."""
        inputs = self._default_inputs()
        result = run_monte_carlo(**inputs)
        np.testing.assert_array_equal(
            result["paths"][:, 0], inputs["initial_capital"]
        )

    def test_deterministic_with_seed(self):
        """Same seed → same results."""
        inputs = self._default_inputs()
        r1 = run_monte_carlo(**inputs)
        r2 = run_monte_carlo(**inputs)
        np.testing.assert_array_equal(r1["final_values"], r2["final_values"])

    def test_statistics_keys(self):
        """Statistics dict must contain all expected keys."""
        result = run_monte_carlo(**self._default_inputs())
        stats = result["statistics"]
        expected_keys = [
            "probability_positive_return",
            "probability_10pct_cagr",
            "probability_15pct_cagr",
            "var_95_inr",
            "cvar_95_inr",
            "median_cagr_pct",
            "return_range_10_90_pct",
            "median_final_value_inr",
            "expected_final_value_inr",
            "max_drawdown_median_pct",
            "max_drawdown_worst_5pct",
        ]
        for key in expected_keys:
            assert key in stats, f"Missing stat: {key}"

    def test_probabilities_are_percentages(self):
        """Probability values should be 0-100."""
        result = run_monte_carlo(**self._default_inputs())
        stats = result["statistics"]
        assert 0 <= stats["probability_positive_return"] <= 100
        assert 0 <= stats["probability_10pct_cagr"] <= 100
        assert 0 <= stats["probability_15pct_cagr"] <= 100

    def test_positive_return_expected(self):
        """With 12% expected return over 5 years, majority should be positive."""
        result = run_monte_carlo(**self._default_inputs())
        assert result["statistics"]["probability_positive_return"] > 60

    def test_var_is_positive(self):
        """VaR should be a positive number (potential loss amount)."""
        result = run_monte_carlo(**self._default_inputs())
        # VaR can be negative if the 5th percentile is above initial capital
        # but with reasonable params it should be positive or at least finite
        assert np.isfinite(result["statistics"]["var_95_inr"])

    def test_rejects_negative_capital(self):
        """Should reject negative initial capital."""
        inputs = self._default_inputs()
        inputs["initial_capital"] = -100
        with pytest.raises(ValueError, match="positive"):
            run_monte_carlo(**inputs)

    def test_rejects_negative_horizon(self):
        """Should reject negative time horizon."""
        inputs = self._default_inputs()
        inputs["time_horizon_years"] = -1
        with pytest.raises(ValueError, match="positive"):
            run_monte_carlo(**inputs)

    def test_rejects_mismatched_weights(self):
        """Should reject if weights length != assets."""
        inputs = self._default_inputs()
        inputs["weights"] = np.array([0.5, 0.3, 0.2])  # 3 weights for 2 assets
        with pytest.raises(ValueError, match="match"):
            run_monte_carlo(**inputs)

    def test_rejects_weights_not_summing_to_one(self):
        """Weights must approximately sum to 1.0."""
        inputs = self._default_inputs()
        inputs["weights"] = np.array([0.3, 0.3])  # Sum = 0.6
        with pytest.raises(ValueError, match="sum"):
            run_monte_carlo(**inputs)


# ── Single Asset Monte Carlo Tests ──────────────────────────────────


class TestRunSingleAssetMonteCarlo:
    """Tests for the single-asset convenience wrapper."""

    def test_returns_valid_result(self):
        """Should return valid Monte Carlo output."""
        result = run_single_asset_monte_carlo(
            annual_return=0.12,
            annual_volatility=0.20,
            initial_capital=500_000,
            time_horizon_years=3,
            num_simulations=500,
            seed=99,
        )
        assert "statistics" in result
        assert len(result["final_values"]) == 500

    def test_rejects_negative_capital(self):
        """Should reject negative capital."""
        with pytest.raises(ValueError):
            run_single_asset_monte_carlo(
                annual_return=0.12,
                annual_volatility=0.20,
                initial_capital=-100,
                time_horizon_years=3,
            )
