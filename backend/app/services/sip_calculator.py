"""
SIP (Systematic Investment Plan) Calculator.

Calculates future value projections for monthly periodic investments.
Supports standard SIP and step-up SIP (annual increase).

The math is fundamentally different from lump-sum portfolio simulation
because SIP is a series of individual investments, each compounding
from its own start date.

Pure math layer — no database, no async.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def calculate_sip_projections(
    monthly_amount: float,
    expected_annual_return: float,
    time_horizon_years: int,
    annual_step_up_pct: float = 0.0,
) -> dict[str, Any]:
    """
    Calculate SIP future value.

    Standard SIP Formula:
        FV = P × [((1+r)^n - 1) / r] × (1+r)
    Where:
        P = Monthly investment
        r = Monthly rate of return (annual / 12)
        n = Total months

    Args:
        monthly_amount: INR invested per month. Must be > 0.
        expected_annual_return: e.g., 0.12 for 12%.
        time_horizon_years: Investment period in whole years. Must be >= 1.
        annual_step_up_pct: Optional: increase SIP by X% yearly. Default 0.

    Returns:
        Dict with projected values, gains, and returns.

    Raises:
        ValueError: If inputs are invalid.
    """
    # Input validation
    if monthly_amount <= 0:
        raise ValueError(f"Monthly amount must be positive, got {monthly_amount}")

    if time_horizon_years < 1:
        raise ValueError(
            f"Time horizon must be at least 1 year, got {time_horizon_years}"
        )

    if expected_annual_return < -0.5 or expected_annual_return > 1.0:
        raise ValueError(
            f"Expected annual return must be between -50% and 100%, "
            f"got {expected_annual_return * 100:.1f}%"
        )

    if annual_step_up_pct < 0 or annual_step_up_pct > 100:
        raise ValueError(
            f"Annual step-up must be 0-100%, got {annual_step_up_pct}%"
        )

    monthly_rate = expected_annual_return / 12
    total_months = time_horizon_years * 12

    if annual_step_up_pct > 0:
        # Step-up SIP: calculate year by year
        total_invested = 0.0
        future_value = 0.0
        current_monthly = monthly_amount
        yearly_breakdown: list[dict[str, Any]] = []

        for year in range(time_horizon_years):
            year_invested = 0.0
            for month in range(12):
                months_remaining = total_months - (year * 12 + month) - 1
                if monthly_rate != 0:
                    future_value += current_monthly * ((1 + monthly_rate) ** months_remaining)
                else:
                    future_value += current_monthly
                total_invested += current_monthly
                year_invested += current_monthly

            yearly_breakdown.append({
                "year": year + 1,
                "monthly_amount": round(current_monthly, 2),
                "year_invested": round(year_invested, 2),
                "cumulative_invested": round(total_invested, 2),
            })

            current_monthly *= (1 + annual_step_up_pct / 100)

    else:
        # Standard SIP formula
        total_invested = monthly_amount * total_months

        if monthly_rate != 0:
            future_value = monthly_amount * (
                ((1 + monthly_rate) ** total_months - 1) / monthly_rate
            ) * (1 + monthly_rate)
        else:
            future_value = total_invested

        yearly_breakdown = []

    wealth_gain = future_value - total_invested

    # Effective XIRR approximation
    if total_invested > 0 and future_value > 0 and time_horizon_years > 0:
        effective_cagr = (
            (future_value / total_invested) ** (1 / time_horizon_years) - 1
        ) * 100
    else:
        effective_cagr = 0.0

    result: dict[str, Any] = {
        "total_invested_inr": round(total_invested, 2),
        "future_value_inr": round(future_value, 2),
        "wealth_gain_inr": round(wealth_gain, 2),
        "absolute_return_pct": round(
            (wealth_gain / total_invested) * 100, 2
        ) if total_invested > 0 else 0.0,
        "effective_cagr_pct": round(effective_cagr, 2),
        "monthly_amount": monthly_amount,
        "time_horizon_years": time_horizon_years,
        "expected_annual_return_pct": round(expected_annual_return * 100, 2),
    }

    if annual_step_up_pct > 0:
        result["annual_step_up_pct"] = annual_step_up_pct
        result["final_monthly_amount"] = round(
            monthly_amount * ((1 + annual_step_up_pct / 100) ** time_horizon_years), 2
        )
        result["yearly_breakdown"] = yearly_breakdown

    return result


def compare_sip_scenarios(
    monthly_amount: float,
    time_horizon_years: int,
    return_scenarios: list[float] | None = None,
) -> list[dict[str, Any]]:
    """
    Compare SIP outcomes across different return scenarios.

    Useful for showing best/expected/worst case on the UI.

    Args:
        monthly_amount: INR invested per month.
        time_horizon_years: Investment period.
        return_scenarios: List of annual returns to compare.
            Defaults to [0.08, 0.10, 0.12, 0.15] (8%, 10%, 12%, 15%).

    Returns:
        List of projection dicts, one per scenario.
    """
    if return_scenarios is None:
        return_scenarios = [0.08, 0.10, 0.12, 0.15]

    return [
        calculate_sip_projections(monthly_amount, r, time_horizon_years)
        for r in return_scenarios
    ]
