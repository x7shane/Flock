"""
Simulation API — Monte Carlo + Historical Stress Test.

These endpoints use pre-generated synthetic data for MVP demo.
In production, they would pull from the DB-stored historical prices.
"""

import numpy as np
from fastapi import APIRouter, HTTPException

from app.schemas.simulate import (
    SimulateRequest,
    SimulateResponse,
    SimulationStatistics,
    StressTestRequest,
    StressTestResponse,
    StressTestResult,
)
from app.services.monte_carlo import run_monte_carlo
from app.services.stress_test import (
    CRISIS_PERIODS,
    get_available_crises,
    run_stress_test,
)

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("", response_model=SimulateResponse)
async def run_simulation(req: SimulateRequest):
    """
    Run Monte Carlo simulation on a portfolio.

    For MVP, uses synthetic return parameters (~12% annual, ~20% vol).
    Production would estimate from actual historical prices in DB.
    """
    n = len(req.tickers)
    if len(req.weights) != n:
        raise HTTPException(400, "Tickers and weights must have same length")

    weights = np.array(req.weights)
    if abs(weights.sum() - 1.0) > 0.05:
        raise HTTPException(400, f"Weights must sum to ~1.0, got {weights.sum():.2f}")

    # MVP: synthetic parameters (production would pull from DB)
    np.random.seed(42)
    expected_returns = np.random.uniform(0.08, 0.16, n)
    vol = np.random.uniform(0.18, 0.30, n)
    cov = np.diag(vol**2)
    # Add mild cross-correlation
    for i in range(n):
        for j in range(i + 1, n):
            corr = 0.3 + np.random.uniform(0, 0.3)
            cov[i, j] = cov[j, i] = corr * vol[i] * vol[j]

    try:
        result = run_monte_carlo(
            expected_returns=expected_returns,
            covariance_matrix=cov,
            weights=weights,
            initial_capital=req.initial_capital,
            time_horizon_years=req.time_horizon_years,
            num_simulations=req.num_simulations,
            seed=42,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return SimulateResponse(
        statistics=SimulationStatistics(**result["statistics"]),
        initial_capital=req.initial_capital,
        time_horizon_years=req.time_horizon_years,
        tickers=req.tickers,
        weights=req.weights,
    )


@router.post("/stress-test", response_model=StressTestResponse)
async def run_stress_test_endpoint(req: StressTestRequest):
    """
    Run historical stress test on a portfolio.

    For MVP, generates synthetic crisis-period prices.
    """
    import pandas as pd

    n = len(req.tickers)
    if len(req.weights) != n:
        raise HTTPException(400, "Tickers and weights must have same length")

    weights = np.array(req.weights)

    # Generate synthetic historical prices spanning all crisis periods
    dates = pd.bdate_range("2007-01-01", "2023-12-31")
    np.random.seed(99)
    prices = {}
    for ticker in req.tickers:
        daily_returns = np.random.normal(0.0004, 0.015, len(dates))
        prices[ticker] = 100 * np.exp(np.cumsum(daily_returns))
    historical_prices = pd.DataFrame(prices, index=dates)

    results = []
    crisis_ids = [req.crisis_id] if req.crisis_id else list(CRISIS_PERIODS.keys())

    for cid in crisis_ids:
        try:
            res = run_stress_test(
                portfolio_tickers=req.tickers,
                portfolio_weights=weights,
                historical_prices=historical_prices,
                crisis_id=cid,
                initial_capital=req.initial_capital,
            )
            results.append(StressTestResult(**res))
        except ValueError as e:
            results.append(StressTestResult(
                crisis_name=CRISIS_PERIODS.get(cid, {}).get("name", cid),
                error=str(e),
            ))

    return StressTestResponse(
        results=results,
        initial_capital=req.initial_capital,
        tickers=req.tickers,
    )


@router.get("/crises")
async def list_crises():
    """List available crisis scenarios for stress testing."""
    return {"crises": get_available_crises()}
