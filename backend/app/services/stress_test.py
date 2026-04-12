"""
Historical Stress Test Engine.

Simulates how a user's portfolio would have performed during past Indian
market crises. Uses actual historical price data to calculate drawdowns,
recovery times, and worst-day losses.

Pure math layer — no database, no async.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── Crisis Period Database ──────────────────────────────────────────

CRISIS_PERIODS: dict[str, dict[str, Any]] = {
    "2008_global_financial_crisis": {
        "name": "2008 Global Financial Crisis",
        "start": "2008-01-01",
        "end": "2009-03-31",
        "peak_to_trough": "2008-01-09 to 2008-10-27",
        "nifty_50_drawdown_pct": -59.9,
        "description": (
            "Global banking collapse. Lehman Brothers failed. "
            "Indian markets fell ~60%."
        ),
    },
    "2013_taper_tantrum": {
        "name": "2013 Taper Tantrum (INR Crash)",
        "start": "2013-05-22",
        "end": "2013-09-30",
        "peak_to_trough": "2013-05-22 to 2013-08-28",
        "nifty_50_drawdown_pct": -14.2,
        "description": (
            "US Fed hinted at tapering QE. FIIs pulled $12B from India. "
            "INR hit ₹68.85/$."
        ),
    },
    "2016_demonetization": {
        "name": "2016 Demonetization",
        "start": "2016-11-08",
        "end": "2017-03-31",
        "peak_to_trough": "2016-11-08 to 2016-12-26",
        "nifty_50_drawdown_pct": -7.8,
        "description": (
            "India banned ₹500 and ₹1000 notes overnight. "
            "Cash-dependent sectors crashed."
        ),
        "worst_sectors": ["real_estate", "consumer_discretionary", "financials"],
    },
    "2020_covid_crash": {
        "name": "2020 COVID Crash",
        "start": "2020-02-19",
        "end": "2020-06-30",
        "peak_to_trough": "2020-02-19 to 2020-03-23",
        "nifty_50_drawdown_pct": -38.4,
        "description": (
            "Global pandemic lockdown. Fastest 30%+ crash in history. "
            "Fastest recovery too."
        ),
    },
    "2022_fii_selloff": {
        "name": "2022 FII Selloff",
        "start": "2022-01-01",
        "end": "2022-06-30",
        "peak_to_trough": "2022-01-18 to 2022-06-17",
        "nifty_50_drawdown_pct": -16.6,
        "description": (
            "FIIs sold ₹2.1 lakh crore in H1 2022. "
            "Highest ever FII outflow."
        ),
    },
}


def get_available_crises() -> list[dict[str, str]]:
    """Return list of available crisis scenarios for the UI."""
    return [
        {
            "id": crisis_id,
            "name": crisis["name"],
            "description": crisis["description"],
            "nifty_50_drawdown_pct": crisis["nifty_50_drawdown_pct"],
        }
        for crisis_id, crisis in CRISIS_PERIODS.items()
    ]


# ── Stress Test Logic ───────────────────────────────────────────────


def run_stress_test(
    portfolio_tickers: list[str],
    portfolio_weights: np.ndarray,
    historical_prices: pd.DataFrame,
    crisis_id: str,
    initial_capital: float,
) -> dict[str, Any]:
    """
    Simulate how the user's portfolio would have performed during a crisis.

    Args:
        portfolio_tickers: List of ticker symbols in the portfolio.
        portfolio_weights: Array of portfolio weights (must sum to ~1.0).
        historical_prices: DataFrame with tickers as columns, dates as index.
            Must contain data spanning the crisis period.
        crisis_id: Key from CRISIS_PERIODS dict.
        initial_capital: Starting capital in INR.

    Returns:
        Dict with drawdown, recovery time, worst day, and narrative summary.

    Raises:
        ValueError: If crisis_id is invalid or data is insufficient.
    """
    # Validate inputs
    if crisis_id not in CRISIS_PERIODS:
        raise ValueError(
            f"Unknown crisis '{crisis_id}'. "
            f"Available: {list(CRISIS_PERIODS.keys())}"
        )

    if initial_capital <= 0:
        raise ValueError(f"Initial capital must be positive, got {initial_capital}")

    if len(portfolio_tickers) != len(portfolio_weights):
        raise ValueError(
            f"Tickers ({len(portfolio_tickers)}) and weights "
            f"({len(portfolio_weights)}) length mismatch"
        )

    weight_sum = np.sum(portfolio_weights)
    if abs(weight_sum - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to ~1.0, got {weight_sum:.4f}")

    crisis = CRISIS_PERIODS[crisis_id]
    start = pd.Timestamp(crisis["start"])
    end = pd.Timestamp(crisis["end"])

    # Check which tickers have data
    available_tickers = [t for t in portfolio_tickers if t in historical_prices.columns]
    if not available_tickers:
        return {
            "crisis_name": crisis["name"],
            "error": "No price data available for any portfolio ticker",
        }

    # Filter prices to crisis period
    crisis_prices = historical_prices.loc[start:end, available_tickers]

    if crisis_prices.empty or len(crisis_prices) < 2:
        return {
            "crisis_name": crisis["name"],
            "error": f"Insufficient price data for {crisis['name']}",
        }

    # Reweight for available tickers
    available_indices = [
        i for i, t in enumerate(portfolio_tickers) if t in available_tickers
    ]
    available_weights = portfolio_weights[available_indices]
    available_weights = available_weights / available_weights.sum()  # Re-normalize

    # Calculate weighted portfolio returns
    daily_returns = crisis_prices.pct_change().dropna()

    if daily_returns.empty:
        return {
            "crisis_name": crisis["name"],
            "error": "Could not compute returns for crisis period",
        }

    portfolio_returns = (daily_returns.values * available_weights).sum(axis=1)
    portfolio_returns = pd.Series(portfolio_returns, index=daily_returns.index)

    # Cumulative portfolio value
    portfolio_value = initial_capital * (1 + portfolio_returns).cumprod()

    # Peak tracking for drawdown calculation
    peak = portfolio_value.expanding().max()
    drawdown = (portfolio_value - peak) / peak

    max_drawdown = float(drawdown.min())
    max_drawdown_date = drawdown.idxmin()

    # Recovery: when does portfolio return to pre-crisis peak?
    pre_crisis_value = portfolio_value.iloc[0]
    recovery_mask = portfolio_value.loc[max_drawdown_date:] >= pre_crisis_value

    if recovery_mask.any():
        recovery_date = recovery_mask.idxmax()
        recovery_days = int((recovery_date - max_drawdown_date).days)
    else:
        recovery_date = None
        recovery_days = None  # Didn't recover within the period

    # Worst single day
    worst_day_return = float(portfolio_returns.min())
    worst_day_date = portfolio_returns.idxmin()

    return {
        "crisis_name": crisis["name"],
        "crisis_description": crisis["description"],
        "portfolio_max_drawdown_pct": round(max_drawdown * 100, 2),
        "max_drawdown_date": str(max_drawdown_date.date()),
        "worst_single_day_pct": round(worst_day_return * 100, 2),
        "worst_single_day_date": str(worst_day_date.date()),
        "recovery_days": recovery_days,
        "recovery_date": (
            str(recovery_date.date()) if recovery_date else "Did not recover in period"
        ),
        "final_value_inr": round(float(portfolio_value.iloc[-1]), 2),
        "loss_at_trough_inr": round(
            float(initial_capital - portfolio_value.min()), 2
        ),
        "nifty_50_drawdown_pct": crisis["nifty_50_drawdown_pct"],
        "tickers_analyzed": available_tickers,
        "tickers_missing": [
            t for t in portfolio_tickers if t not in available_tickers
        ],
    }


def run_all_stress_tests(
    portfolio_tickers: list[str],
    portfolio_weights: np.ndarray,
    historical_prices: pd.DataFrame,
    initial_capital: float,
) -> list[dict[str, Any]]:
    """
    Run stress tests against ALL available crisis periods.

    Returns:
        List of stress test results, one per crisis.
    """
    results = []
    for crisis_id in CRISIS_PERIODS:
        try:
            result = run_stress_test(
                portfolio_tickers, portfolio_weights,
                historical_prices, crisis_id, initial_capital,
            )
            results.append(result)
        except Exception as e:
            logger.error("Stress test %s failed: %s", crisis_id, e)
            results.append({
                "crisis_name": CRISIS_PERIODS[crisis_id]["name"],
                "error": str(e),
            })
    return results
