"""
Pydantic schemas for simulation API (Monte Carlo + Stress Test).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SimulateRequest(BaseModel):
    """Request body for Monte Carlo simulation."""
    tickers: list[str] = Field(..., min_length=1, description="Stock tickers")
    weights: list[float] = Field(..., min_length=1, description="Portfolio weights (must sum to ~1.0)")
    initial_capital: float = Field(..., gt=0, description="Starting capital in INR")
    time_horizon_years: float = Field(..., gt=0, le=30, description="Investment period in years")
    num_simulations: int = Field(10_000, ge=100, le=50_000, description="Number of MC paths")


class SimulationStatistics(BaseModel):
    """Monte Carlo output statistics."""
    probability_positive_return: float
    probability_10pct_cagr: float
    probability_15pct_cagr: float
    var_95_inr: float
    cvar_95_inr: float
    median_cagr_pct: float
    return_range_10_90_pct: list[float]
    median_final_value_inr: float
    expected_final_value_inr: float
    max_drawdown_median_pct: float
    max_drawdown_worst_5pct: float


class SimulateResponse(BaseModel):
    """Monte Carlo simulation result."""
    statistics: SimulationStatistics
    initial_capital: float
    time_horizon_years: float
    tickers: list[str]
    weights: list[float]


class StressTestRequest(BaseModel):
    """Request body for historical stress test."""
    tickers: list[str] = Field(..., min_length=1)
    weights: list[float] = Field(..., min_length=1)
    initial_capital: float = Field(..., gt=0)
    crisis_id: str | None = Field(None, description="Specific crisis ID, or None for all")


class StressTestResult(BaseModel):
    """Single crisis stress test result."""
    crisis_name: str
    crisis_description: str | None = None
    portfolio_max_drawdown_pct: float | None = None
    max_drawdown_date: str | None = None
    worst_single_day_pct: float | None = None
    worst_single_day_date: str | None = None
    recovery_days: int | None = None
    recovery_date: str | None = None
    final_value_inr: float | None = None
    loss_at_trough_inr: float | None = None
    nifty_50_drawdown_pct: float | None = None
    error: str | None = None


class StressTestResponse(BaseModel):
    """Stress test results."""
    results: list[StressTestResult]
    initial_capital: float
    tickers: list[str]
