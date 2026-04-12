"""
Monte Carlo Simulation Engine.

Portfolio-level Monte Carlo using Geometric Brownian Motion (GBM).
Generates 10,000 simulated paths to produce probability-based outcomes
for a user's portfolio.

Pure math layer — no database, no async. Stateless and unit-testable.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ── Return Parameter Estimation ─────────────────────────────────────


def estimate_return_parameters(
    price_series: pd.Series,
    min_years: int = 3,
) -> tuple[float, float]:
    """
    Estimate annualized expected return and volatility from historical prices.

    Uses log returns for mathematical consistency with GBM.

    Args:
        price_series: Daily closing prices (DatetimeIndex).
        min_years: Minimum years of data required.

    Returns:
        (annual_expected_return, annual_volatility)

    Raises:
        ValueError: If insufficient data.
    """
    if price_series is None or len(price_series) == 0:
        raise ValueError("Empty price series provided")

    trading_days = len(price_series)
    years_of_data = trading_days / 252

    if years_of_data < min_years:
        raise ValueError(
            f"Need {min_years}+ years of data, got {years_of_data:.1f} years "
            f"({trading_days} trading days)"
        )

    # Log returns
    log_returns = np.log(price_series / price_series.shift(1)).dropna()

    if len(log_returns) == 0:
        raise ValueError("Price series produced no valid log returns")

    # Annualize
    daily_mean = log_returns.mean()
    daily_std = log_returns.std()

    annual_return = float(daily_mean * 252)
    annual_volatility = float(daily_std * np.sqrt(252))

    return annual_return, annual_volatility


# ── Covariance Matrix Construction ──────────────────────────────────


def build_covariance_matrix(
    price_dataframe: pd.DataFrame,
) -> np.ndarray:
    """
    Build annualized covariance matrix from daily prices.

    Args:
        price_dataframe: DataFrame with tickers as columns, dates as index.
            Must have at least 2 columns and 252 rows.

    Returns:
        Annualized covariance matrix (N × N).

    Raises:
        ValueError: If insufficient data.
    """
    if price_dataframe.empty:
        raise ValueError("Empty price DataFrame provided")

    if len(price_dataframe.columns) < 2:
        raise ValueError("Need at least 2 assets for covariance matrix")

    if len(price_dataframe) < 252:
        raise ValueError(
            f"Need at least 252 data points, got {len(price_dataframe)}"
        )

    log_returns = np.log(price_dataframe / price_dataframe.shift(1)).dropna()
    cov_daily = log_returns.cov()

    # Annualize: multiply by 252 trading days
    cov_annual = cov_daily * 252

    return cov_annual.values


# ── Monte Carlo Simulation ──────────────────────────────────────────


def run_monte_carlo(
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    weights: np.ndarray,
    initial_capital: float,
    time_horizon_years: float,
    num_simulations: int = 10_000,
    time_steps_per_year: int = 252,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Run portfolio-level Monte Carlo simulation using correlated GBM.

    Args:
        expected_returns: Shape (N,) — annual expected return per asset.
        covariance_matrix: Shape (N, N) — annual covariance matrix.
        weights: Shape (N,) — portfolio weights, must sum to ~1.0.
        initial_capital: Starting capital in INR.
        time_horizon_years: Investment period in years.
        num_simulations: Number of Monte Carlo paths.
        time_steps_per_year: Trading days per year.
        seed: Random seed for reproducibility.

    Returns:
        Dict with:
            - final_values: array of terminal portfolio values
            - paths: array of portfolio value paths
            - statistics: dict of summary statistics

    Raises:
        ValueError: If inputs are invalid.
    """
    _validate_inputs(
        expected_returns, covariance_matrix, weights,
        initial_capital, time_horizon_years,
    )

    np.random.seed(seed)

    total_steps = int(time_horizon_years * time_steps_per_year)
    dt = 1 / time_steps_per_year

    # Portfolio-level parameters
    portfolio_return = float(weights @ expected_returns)
    portfolio_vol = float(np.sqrt(weights @ covariance_matrix @ weights))

    # GBM path generation (portfolio level)
    Z = np.random.standard_normal((num_simulations, total_steps))

    drift = (portfolio_return - 0.5 * portfolio_vol**2) * dt
    diffusion = portfolio_vol * np.sqrt(dt) * Z

    log_returns = drift + diffusion
    cumulative_returns = np.cumsum(log_returns, axis=1)

    paths = initial_capital * np.exp(cumulative_returns)

    # Prepend initial capital
    paths = np.column_stack([np.full(num_simulations, initial_capital), paths])

    final_values = paths[:, -1]

    # Calculate statistics
    statistics = _calculate_statistics(
        final_values, paths, initial_capital, time_horizon_years
    )

    return {
        "final_values": final_values,
        "paths": paths,
        "statistics": statistics,
    }


# ── Single-Asset Monte Carlo ───────────────────────────────────────


def run_single_asset_monte_carlo(
    annual_return: float,
    annual_volatility: float,
    initial_capital: float,
    time_horizon_years: float,
    num_simulations: int = 10_000,
    time_steps_per_year: int = 252,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Simplified Monte Carlo for a single asset (no covariance needed).

    Convenience wrapper for single-stock or single-fund analysis.
    """
    if initial_capital <= 0:
        raise ValueError(f"Initial capital must be positive, got {initial_capital}")
    if time_horizon_years <= 0:
        raise ValueError(f"Time horizon must be positive, got {time_horizon_years}")

    return run_monte_carlo(
        expected_returns=np.array([annual_return]),
        covariance_matrix=np.array([[annual_volatility**2]]),
        weights=np.array([1.0]),
        initial_capital=initial_capital,
        time_horizon_years=time_horizon_years,
        num_simulations=num_simulations,
        time_steps_per_year=time_steps_per_year,
        seed=seed,
    )


# ── Statistics ──────────────────────────────────────────────────────


def _calculate_statistics(
    final_values: np.ndarray,
    paths: np.ndarray,
    initial_capital: float,
    time_horizon_years: float,
) -> dict[str, Any]:
    """Calculate all user-facing statistics from Monte Carlo results."""

    returns = (final_values - initial_capital) / initial_capital
    cagr_values = (final_values / initial_capital) ** (1 / time_horizon_years) - 1

    # Probability of target returns
    prob_positive = float(np.mean(returns > 0) * 100)
    prob_10pct = float(np.mean(cagr_values > 0.10) * 100)
    prob_15pct = float(np.mean(cagr_values > 0.15) * 100)

    # Value at Risk (VaR) — 95% confidence
    # "In 95% of scenarios, you won't lose more than ₹X"
    var_95 = float(initial_capital - np.percentile(final_values, 5))

    # Conditional VaR (Expected Shortfall) — average loss in worst 5%
    worst_5pct = final_values[final_values <= np.percentile(final_values, 5)]
    cvar_95 = float(initial_capital - np.mean(worst_5pct)) if len(worst_5pct) > 0 else 0.0

    # Max Drawdown (across all paths)
    peak = np.maximum.accumulate(paths, axis=1)
    drawdowns = (peak - paths) / peak
    max_drawdown_per_path = np.max(drawdowns, axis=1)

    # Return range (10th to 90th percentile)
    return_p10 = float(np.percentile(cagr_values, 10) * 100)
    return_p50 = float(np.percentile(cagr_values, 50) * 100)
    return_p90 = float(np.percentile(cagr_values, 90) * 100)

    return {
        "probability_positive_return": round(prob_positive, 1),
        "probability_10pct_cagr": round(prob_10pct, 1),
        "probability_15pct_cagr": round(prob_15pct, 1),
        "var_95_inr": round(var_95, 2),
        "cvar_95_inr": round(cvar_95, 2),
        "median_cagr_pct": round(return_p50, 2),
        "return_range_10_90_pct": [round(return_p10, 2), round(return_p90, 2)],
        "median_final_value_inr": round(float(np.median(final_values)), 2),
        "expected_final_value_inr": round(float(np.mean(final_values)), 2),
        "max_drawdown_median_pct": round(float(np.median(max_drawdown_per_path) * 100), 2),
        "max_drawdown_worst_5pct": round(float(np.percentile(max_drawdown_per_path, 95) * 100), 2),
    }


# ── Validation ──────────────────────────────────────────────────────


def _validate_inputs(
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    weights: np.ndarray,
    initial_capital: float,
    time_horizon_years: float,
) -> None:
    """Validate Monte Carlo inputs."""
    n = len(expected_returns)

    if initial_capital <= 0:
        raise ValueError(f"Initial capital must be positive, got {initial_capital}")

    if time_horizon_years <= 0:
        raise ValueError(f"Time horizon must be positive, got {time_horizon_years}")

    if covariance_matrix.shape != (n, n):
        raise ValueError(
            f"Covariance matrix shape {covariance_matrix.shape} doesn't match "
            f"{n} assets"
        )

    if len(weights) != n:
        raise ValueError(
            f"Weights length {len(weights)} doesn't match {n} assets"
        )

    weight_sum = np.sum(weights)
    if abs(weight_sum - 1.0) > 0.01:
        raise ValueError(
            f"Weights must sum to ~1.0, got {weight_sum:.4f}"
        )

    if np.any(np.isnan(expected_returns)):
        raise ValueError("Expected returns contain NaN values")

    if np.any(np.isnan(covariance_matrix)):
        raise ValueError("Covariance matrix contains NaN values")
