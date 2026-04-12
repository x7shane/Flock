"""
Pydantic schemas for SIP calculator API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SipRequest(BaseModel):
    """Request body for SIP projection."""
    monthly_amount: float = Field(..., gt=0, description="Monthly SIP amount in INR")
    expected_annual_return: float = Field(..., ge=-0.5, le=1.0, description="Expected annual return (e.g. 0.12 for 12%)")
    time_horizon_years: int = Field(..., ge=1, le=50, description="Investment period in years")
    annual_step_up_pct: float = Field(0.0, ge=0, le=100, description="Annual increase in SIP amount (%)")


class YearlyBreakdown(BaseModel):
    """One year's SIP details (for step-up SIP)."""
    year: int
    monthly_amount: float
    year_invested: float
    cumulative_invested: float


class SipResponse(BaseModel):
    """SIP projection result."""
    total_invested_inr: float
    future_value_inr: float
    wealth_gain_inr: float
    absolute_return_pct: float
    effective_cagr_pct: float
    monthly_amount: float
    time_horizon_years: int
    expected_annual_return_pct: float
    annual_step_up_pct: float | None = None
    final_monthly_amount: float | None = None
    yearly_breakdown: list[YearlyBreakdown] | None = None


class SipCompareRequest(BaseModel):
    """Request to compare SIP scenarios."""
    monthly_amount: float = Field(..., gt=0)
    time_horizon_years: int = Field(..., ge=1, le=50)
    return_scenarios: list[float] | None = Field(None, description="List of annual returns to compare")


class SipCompareResponse(BaseModel):
    """Multiple SIP scenario results."""
    scenarios: list[SipResponse]
