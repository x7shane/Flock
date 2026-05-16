"""
Tests for Flock Score Scoring Engine — Pure Math Layer.

No mocking needed. These tests validate the mathematical correctness of
factor normalization, pillar aggregation, and weighted scoring.
"""

import numpy as np
import pandas as pd
import pytest

from app.services.scoring_engine import (
    FACTOR_DIRECTION,
    PILLARS,
    PRESETS,
    calculate_flock_score,
    calculate_pillar_score,
    normalize_factor,
    score_all_stocks,
)


# ── Normalization Tests ─────────────────────────────────────────────


class TestNormalizeFactor:
    """Tests for percentile-rank normalization."""

    def test_higher_is_better_top_value(self):
        """Highest value in universe should get ~100 percentile."""
        values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        result = normalize_factor(values, 50.0, higher_is_better=True)
        assert result == 100.0

    def test_higher_is_better_bottom_value(self):
        """Lowest value gets lowest percentile."""
        values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        result = normalize_factor(values, 10.0, higher_is_better=True)
        assert result == 20.0  # 1/5 = 20th percentile (rank method)

    def test_lower_is_better_inverts(self):
        """When lower is better, low raw value → high percentile."""
        values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        # Lowest value (10) with lower_is_better should get the HIGHEST score
        result = normalize_factor(values, 10.0, higher_is_better=False)
        assert result == 80.0  # 100 - 20 = 80

    def test_lower_is_better_top_raw_value(self):
        """When lower is better, highest raw value → lowest score."""
        values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        result = normalize_factor(values, 50.0, higher_is_better=False)
        assert result == 0.0  # 100 - 100 = 0

    def test_none_returns_none(self):
        """None ticker value returns None."""
        values = np.array([10.0, 20.0, 30.0])
        assert normalize_factor(values, None, higher_is_better=True) is None

    def test_nan_returns_none(self):
        """NaN ticker value returns None."""
        values = np.array([10.0, 20.0, 30.0])
        assert normalize_factor(values, float("nan"), higher_is_better=True) is None

    def test_empty_universe_returns_none(self):
        """Empty universe array returns None."""
        values = np.array([], dtype=float)
        assert normalize_factor(values, 10.0, higher_is_better=True) is None

    def test_nans_in_universe_excluded(self):
        """NaN values in universe are excluded from ranking."""
        values = np.array([10.0, float("nan"), 30.0, float("nan"), 50.0])
        result = normalize_factor(values, 30.0, higher_is_better=True)
        # 3 clean values: [10, 30, 50]. 30 is 2nd of 3 → ~66.67 percentile
        assert result is not None
        assert 60.0 <= result <= 70.0


# ── Pillar Score Tests ──────────────────────────────────────────────


class TestCalculatePillarScore:
    """Tests for pillar aggregation."""

    def test_averages_valid_scores(self):
        """Average of valid factor percentiles."""
        factor_scores = {"roe": 80.0, "roce": 60.0, "net_profit_margin": 40.0}
        result = calculate_pillar_score(factor_scores, ["roe", "roce", "net_profit_margin"])
        assert result == 60.0  # (80 + 60 + 40) / 3

    def test_excludes_none_values(self):
        """None factors excluded from average."""
        factor_scores = {"roe": 80.0, "roce": None, "net_profit_margin": 40.0}
        result = calculate_pillar_score(factor_scores, ["roe", "roce", "net_profit_margin"])
        assert result == 60.0  # (80 + 40) / 2

    def test_all_none_returns_none(self):
        """All-None pillar → None."""
        factor_scores = {"roe": None, "roce": None, "net_profit_margin": None}
        result = calculate_pillar_score(factor_scores, ["roe", "roce", "net_profit_margin"])
        assert result is None

    def test_missing_factor_key_treated_as_none(self):
        """Factor not in dict treated as missing."""
        factor_scores = {"roe": 80.0}  # roce and net_profit_margin missing
        result = calculate_pillar_score(factor_scores, ["roe", "roce", "net_profit_margin"])
        assert result == 80.0  # Only roe available


# ── Flock Score Tests ───────────────────────────────────────────────


class TestCalculateFlockScore:
    """Tests for final Flock Score calculation."""

    def test_balanced_preset(self):
        """Correct weighted sum with balanced weights."""
        pillar_scores = {
            "profitability": 80.0,
            "growth": 60.0,
            "health": 70.0,
            "valuation": 50.0,
            "quality": 40.0,
        }
        weights = PRESETS["balanced"]
        result = calculate_flock_score(pillar_scores, weights)

        # Manual: 80*0.20 + 60*0.20 + 70*0.25 + 50*0.20 + 40*0.15
        #       = 16 + 12 + 17.5 + 10 + 6 = 61.5
        assert result == 61.5

    def test_renormalization_on_missing_pillar(self):
        """Weight redistribution when a pillar is None."""
        pillar_scores = {
            "profitability": 80.0,
            "growth": None,  # Missing entirely
            "health": 70.0,
            "valuation": 50.0,
            "quality": 40.0,
        }
        weights = PRESETS["balanced"]
        result = calculate_flock_score(pillar_scores, weights)

        # Available: profitability(0.20), health(0.25), valuation(0.20), quality(0.15)
        # Total available weight = 0.80
        # Renormalized: 0.20/0.80=0.25, 0.25/0.80=0.3125, 0.20/0.80=0.25, 0.15/0.80=0.1875
        # Score: 80*0.25 + 70*0.3125 + 50*0.25 + 40*0.1875
        #      = 20 + 21.875 + 12.5 + 7.5 = 61.875
        assert result == 61.88  # Rounded to 2dp

    def test_no_data_returns_zero(self):
        """All pillars None → 0.0."""
        pillar_scores = {
            "profitability": None,
            "growth": None,
            "health": None,
            "valuation": None,
            "quality": None,
        }
        result = calculate_flock_score(pillar_scores, PRESETS["balanced"])
        assert result == 0.0

    def test_single_pillar_available(self):
        """Only one pillar present → that pillar's score IS the Flock Score."""
        pillar_scores = {
            "profitability": 75.0,
            "growth": None,
            "health": None,
            "valuation": None,
            "quality": None,
        }
        result = calculate_flock_score(pillar_scores, PRESETS["balanced"])
        assert result == 75.0


# ── Config Integrity Tests ──────────────────────────────────────────


class TestConfigIntegrity:
    """Validate that scoring config is complete and consistent."""

    def test_factor_direction_covers_all_16_factors(self):
        """All 16 factors must be in FACTOR_DIRECTION."""
        assert len(FACTOR_DIRECTION) == 16

    def test_all_pillar_factors_exist_in_direction_map(self):
        """Every factor in PILLARS must have a direction in FACTOR_DIRECTION."""
        all_pillar_factors = set()
        for factors in PILLARS.values():
            all_pillar_factors.update(factors)
        for factor in all_pillar_factors:
            assert factor in FACTOR_DIRECTION, f"{factor} missing from FACTOR_DIRECTION"

    def test_no_orphan_factors(self):
        """Every factor in FACTOR_DIRECTION must be assigned to exactly one pillar."""
        all_pillar_factors = set()
        for factors in PILLARS.values():
            all_pillar_factors.update(factors)
        for factor in FACTOR_DIRECTION:
            assert factor in all_pillar_factors, f"{factor} not assigned to any pillar"

    def test_no_duplicate_factors_across_pillars(self):
        """No factor should appear in multiple pillars."""
        seen = set()
        for factors in PILLARS.values():
            for factor in factors:
                assert factor not in seen, f"{factor} appears in multiple pillars"
                seen.add(factor)

    def test_preset_weights_sum_to_one(self):
        """Each preset's weights must sum to 1.0."""
        for preset_name, weights in PRESETS.items():
            total = sum(weights.values())
            assert abs(total - 1.0) < 1e-9, f"Preset '{preset_name}' sums to {total}"

    def test_preset_weights_cover_all_pillars(self):
        """Each preset must have weights for all 5 pillars."""
        pillar_names = set(PILLARS.keys())
        for preset_name, weights in PRESETS.items():
            assert set(weights.keys()) == pillar_names, (
                f"Preset '{preset_name}' missing pillars: {pillar_names - set(weights.keys())}"
            )


# ── Batch Scoring Tests ─────────────────────────────────────────────


class TestScoreAllStocks:
    """Tests for the batch scoring entry point."""

    def test_empty_dataframe_returns_empty(self):
        """Empty input → empty output."""
        result = score_all_stocks(pd.DataFrame())
        assert result.empty

    def test_output_shape(self):
        """Output has correct columns for 2 stocks."""
        df = pd.DataFrame([
            {"stock_id": 1, "roe": 0.15, "roce": 0.18, "pe_ratio": 22.0, "debt_equity": 0.5},
            {"stock_id": 2, "roe": 0.10, "roce": 0.12, "pe_ratio": 35.0, "debt_equity": 1.2},
        ])
        result = score_all_stocks(df)
        assert len(result) == 2
        assert "stock_id" in result.columns
        assert "score_balanced" in result.columns
        assert "pillar_profitability" in result.columns

    def test_higher_roe_gets_higher_profitability_score(self):
        """Stock with higher ROE should rank higher on profitability pillar."""
        df = pd.DataFrame([
            {"stock_id": 1, "roe": 0.25, "roce": 0.20, "net_profit_margin": 0.15},
            {"stock_id": 2, "roe": 0.10, "roce": 0.08, "net_profit_margin": 0.05},
            {"stock_id": 3, "roe": 0.18, "roce": 0.14, "net_profit_margin": 0.10},
        ])
        result = score_all_stocks(df)

        stock1 = result[result["stock_id"] == 1].iloc[0]
        stock2 = result[result["stock_id"] == 2].iloc[0]
        assert stock1["pillar_profitability"] > stock2["pillar_profitability"]

    def test_lower_pe_gets_higher_valuation_score(self):
        """Stock with lower P/E should rank higher on valuation pillar."""
        df = pd.DataFrame([
            {"stock_id": 1, "pe_ratio": 12.0, "pb_ratio": 1.5, "peg_ratio": 0.8},
            {"stock_id": 2, "pe_ratio": 45.0, "pb_ratio": 5.0, "peg_ratio": 2.5},
            {"stock_id": 3, "pe_ratio": 28.0, "pb_ratio": 3.0, "peg_ratio": 1.5},
        ])
        result = score_all_stocks(df)

        stock1 = result[result["stock_id"] == 1].iloc[0]
        stock2 = result[result["stock_id"] == 2].iloc[0]
        assert stock1["pillar_valuation"] > stock2["pillar_valuation"]
