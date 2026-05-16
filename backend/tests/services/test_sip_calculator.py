"""
Tests for SIP (Systematic Investment Plan) Calculator.

Pure math tests — no mocking needed.
"""

import pytest

from app.services.sip_calculator import (
    calculate_sip_projections,
    compare_sip_scenarios,
)


# ── Standard SIP Tests ──────────────────────────────────────────────


class TestCalculateSipProjections:
    """Tests for SIP projection calculations."""

    def test_basic_sip_returns_correct_keys(self):
        """Output should contain all required financial metrics."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        assert "total_invested_inr" in result
        assert "future_value_inr" in result
        assert "wealth_gain_inr" in result
        assert "absolute_return_pct" in result
        assert "effective_cagr_pct" in result

    def test_total_invested_is_correct(self):
        """Total invested = monthly × 12 × years."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        assert result["total_invested_inr"] == 10_000 * 12 * 10  # ₹12,00,000

    def test_future_value_exceeds_invested(self):
        """With positive returns, future value must exceed invested amount."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        assert result["future_value_inr"] > result["total_invested_inr"]

    def test_wealth_gain_is_positive(self):
        """Wealth gain = future value - invested. Should be positive."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        assert result["wealth_gain_inr"] > 0

    def test_zero_return_equals_invested(self):
        """At 0% return, future value should approximately equal invested."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.0,
            time_horizon_years=5,
        )
        assert abs(result["future_value_inr"] - result["total_invested_inr"]) < 1

    def test_known_sip_value(self):
        """Verify against a known SIP calculation.

        ₹10,000/month at 12% for 10 years.
        Standard formula: FV = P × [((1+r)^n - 1) / r] × (1+r)
        r = 0.01 (monthly), n = 120
        FV ≈ ₹23,23,391
        """
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        # Allow 1% tolerance for rounding
        assert 2_300_000 < result["future_value_inr"] < 2_350_000


# ── Step-Up SIP Tests ───────────────────────────────────────────────


class TestStepUpSip:
    """Tests for step-up SIP (annual increase)."""

    def test_step_up_increases_investment(self):
        """With step-up, total invested should exceed standard SIP."""
        standard = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
        )
        step_up = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=10,
            annual_step_up_pct=10,
        )
        assert step_up["total_invested_inr"] > standard["total_invested_inr"]

    def test_step_up_has_yearly_breakdown(self):
        """Step-up SIP should include yearly breakdown."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=5,
            annual_step_up_pct=10,
        )
        assert "yearly_breakdown" in result
        assert len(result["yearly_breakdown"]) == 5

    def test_step_up_yearly_amount_increases(self):
        """Each year's monthly amount should exceed previous year's."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=5,
            annual_step_up_pct=10,
        )
        amounts = [y["monthly_amount"] for y in result["yearly_breakdown"]]
        for i in range(1, len(amounts)):
            assert amounts[i] > amounts[i - 1]

    def test_step_up_final_monthly(self):
        """Final monthly amount should reflect step-up compound."""
        result = calculate_sip_projections(
            monthly_amount=10_000,
            expected_annual_return=0.12,
            time_horizon_years=5,
            annual_step_up_pct=10,
        )
        # 10000 × 1.10^5 ≈ 16105.10
        assert abs(result["final_monthly_amount"] - 16105.10) < 1


# ── Validation Tests ────────────────────────────────────────────────


class TestSipValidation:
    """Tests for input validation."""

    def test_rejects_negative_amount(self):
        """Should reject negative monthly amount."""
        with pytest.raises(ValueError, match="positive"):
            calculate_sip_projections(-1000, 0.12, 10)

    def test_rejects_zero_amount(self):
        """Should reject zero monthly amount."""
        with pytest.raises(ValueError, match="positive"):
            calculate_sip_projections(0, 0.12, 10)

    def test_rejects_zero_years(self):
        """Should reject zero time horizon."""
        with pytest.raises(ValueError, match="at least 1"):
            calculate_sip_projections(10_000, 0.12, 0)

    def test_rejects_extreme_return(self):
        """Should reject unreasonably high expected return."""
        with pytest.raises(ValueError, match="between"):
            calculate_sip_projections(10_000, 2.0, 10)  # 200% return


# ── Scenario Comparison Tests ───────────────────────────────────────


class TestCompareSipScenarios:
    """Tests for scenario comparison."""

    def test_returns_four_scenarios_by_default(self):
        """Default scenarios: 8%, 10%, 12%, 15%."""
        results = compare_sip_scenarios(10_000, 10)
        assert len(results) == 4

    def test_higher_return_higher_value(self):
        """Higher expected return → higher future value."""
        results = compare_sip_scenarios(10_000, 10)
        future_values = [r["future_value_inr"] for r in results]
        for i in range(1, len(future_values)):
            assert future_values[i] > future_values[i - 1]

    def test_custom_scenarios(self):
        """Should accept custom return scenarios."""
        results = compare_sip_scenarios(10_000, 10, [0.05, 0.20])
        assert len(results) == 2
