"""
Flock Score — Fundamental Scoring Engine.

Pure math layer: no database, no async. Stateless and unit-testable.

Pipeline:
    Raw Fundamentals (16 factors)
        → Per-Factor Normalization (percentile rank within Nifty 200)
        → Pillar Aggregation (weighted average within each pillar)
        → Final Score (weighted sum of pillar scores × preset weights)
        → Flock Score: 0–100
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

logger = logging.getLogger(__name__)

# ── Factor Direction Map ────────────────────────────────────────────
# True  = higher raw value → higher (better) score
# False = lower raw value  → higher (better) score

FACTOR_DIRECTION: dict[str, bool] = {
    # Profitability — higher is better
    "roe": True,
    "roce": True,
    "net_profit_margin": True,
    # Growth — higher is better
    "revenue_cagr_3yr": True,
    "eps_growth_3yr": True,
    # Health — mixed
    "debt_equity": False,       # lower debt = safer
    "current_ratio": True,      # higher = more liquid
    "interest_coverage": True,  # higher = can pay interest easily
    "free_cash_flow": True,     # more free cash = better
    # Valuation — lower is cheaper
    "pe_ratio": False,          # lower P/E = cheaper
    "pb_ratio": False,          # lower P/B = cheaper
    "peg_ratio": False,         # lower PEG = undervalued grower
    "dividend_yield": True,     # higher yield = more cash returned
    # Quality
    "promoter_holding_pct": True,   # higher = more skin in the game
    "promoter_pledge_pct": False,   # lower pledge = less risk
    "fii_dii_trend": True,          # increasing = smart money buying
}

# ── Pillar Definitions ──────────────────────────────────────────────

PILLARS: dict[str, list[str]] = {
    "profitability": ["roe", "roce", "net_profit_margin"],
    "growth": ["revenue_cagr_3yr", "eps_growth_3yr"],
    "health": ["debt_equity", "current_ratio", "interest_coverage", "free_cash_flow"],
    "valuation": ["pe_ratio", "pb_ratio", "peg_ratio", "dividend_yield"],
    "quality": ["promoter_holding_pct", "promoter_pledge_pct", "fii_dii_trend"],
}

# ── Preset Weights ──────────────────────────────────────────────────
# Each preset maps pillar → weight (must sum to 1.0).

PRESETS: dict[str, dict[str, float]] = {
    "balanced": {
        "profitability": 0.20,
        "growth": 0.20,
        "health": 0.25,
        "valuation": 0.20,
        "quality": 0.15,
    },
    "growth": {
        "profitability": 0.15,
        "growth": 0.35,
        "health": 0.15,
        "valuation": 0.15,
        "quality": 0.20,
    },
    "value": {
        "profitability": 0.20,
        "growth": 0.10,
        "health": 0.25,
        "valuation": 0.35,
        "quality": 0.10,
    },
    "conservative": {
        "profitability": 0.25,
        "growth": 0.10,
        "health": 0.35,
        "valuation": 0.15,
        "quality": 0.15,
    },
}


# ── Normalization ───────────────────────────────────────────────────


def normalize_factor(
    values: np.ndarray,
    ticker_value: float | None,
    higher_is_better: bool = True,
) -> float | None:
    """
    Normalize a single factor value to 0-100 percentile rank.

    Args:
        values: Array of all stock values for this factor in the universe.
        ticker_value: The specific stock's value for this factor.
        higher_is_better: True for ROE, ROCE. False for Debt/Equity, P/E.

    Returns:
        Percentile score 0-100 (higher = better for that factor), or None.
    """
    if ticker_value is None:
        return None

    try:
        tv = float(ticker_value)
    except (ValueError, TypeError):
        return None

    if np.isnan(tv):
        return None

    # Remove NaN from the universe for ranking
    clean_values = values[~np.isnan(values)]
    if len(clean_values) == 0:
        return None

    percentile = percentileofscore(clean_values, tv, kind="rank")

    if not higher_is_better:
        percentile = 100.0 - percentile

    return round(percentile, 2)


# ── Pillar Aggregation ──────────────────────────────────────────────


def calculate_pillar_score(
    factor_scores: dict[str, float | None],
    pillar_factors: list[str],
) -> float | None:
    """
    Average the factor percentile scores within a pillar, excluding None values.

    Args:
        factor_scores: Dict of factor_name → percentile score (0-100 or None).
        pillar_factors: List of factor names belonging to this pillar.

    Returns:
        Pillar score 0-100, or None if all factors are missing.
    """
    valid_scores = [
        factor_scores[f]
        for f in pillar_factors
        if f in factor_scores and factor_scores[f] is not None
    ]

    if not valid_scores:
        return None

    return round(sum(valid_scores) / len(valid_scores), 2)


# ── Final Flock Score ───────────────────────────────────────────────


def calculate_flock_score(
    pillar_scores: dict[str, float | None],
    weights: dict[str, float],
) -> float | None:
    """
    Weighted sum of pillar scores, re-normalized if any pillar is missing.

    Args:
        pillar_scores: Dict of pillar_name → score (0-100 or None).
        weights: Dict of pillar_name → weight (should sum to 1.0).

    Returns:
        Flock Score 0-100. Higher = fundamentally stronger.
    """
    valid_pillars = {
        p: score
        for p, score in pillar_scores.items()
        if score is not None and p in weights
    }

    if not valid_pillars:
        return None  # No data at all — return null, not a misleading 0

    # Re-normalize weights to sum to 1.0 (handles missing pillars)
    total_weight = sum(weights[p] for p in valid_pillars)
    if total_weight == 0:
        return 0.0

    score = sum(
        valid_pillars[p] * (weights[p] / total_weight)
        for p in valid_pillars
    )

    return round(score, 2)


# ── Batch Scoring ───────────────────────────────────────────────────


def score_all_stocks(
    fundamentals_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Score the entire universe of stocks from raw fundamentals.

    Args:
        fundamentals_df: DataFrame with one row per stock.
            - Must have a 'stock_id' column.
            - Must have columns matching FACTOR_DIRECTION keys.

    Returns:
        DataFrame with columns:
            stock_id, score_balanced, score_growth, score_value, score_conservative,
            pillar_profitability, pillar_growth, pillar_health, pillar_valuation, pillar_quality
    """
    if fundamentals_df.empty:
        return pd.DataFrame(columns=[
            "stock_id",
            "score_balanced", "score_growth", "score_value", "score_conservative",
            "pillar_profitability", "pillar_growth", "pillar_health",
            "pillar_valuation", "pillar_quality",
        ])

    all_factors = list(FACTOR_DIRECTION.keys())
    results: list[dict[str, Any]] = []

    # Build universe arrays for each factor (for percentile ranking)
    universe: dict[str, np.ndarray] = {}
    for factor in all_factors:
        if factor in fundamentals_df.columns:
            universe[factor] = pd.to_numeric(
                fundamentals_df[factor], errors="coerce"
            ).to_numpy(dtype=float)
        else:
            universe[factor] = np.array([], dtype=float)

    # Score each stock
    for _, row in fundamentals_df.iterrows():
        stock_id = row["stock_id"]

        # Step 1: Normalize all factors → percentile scores
        factor_scores: dict[str, float | None] = {}
        for factor in all_factors:
            raw_value = row.get(factor)
            if factor in universe and len(universe[factor]) > 0:
                factor_scores[factor] = normalize_factor(
                    universe[factor],
                    raw_value,
                    higher_is_better=FACTOR_DIRECTION[factor],
                )
            else:
                factor_scores[factor] = None

        # Step 2: Calculate pillar scores
        pillar_scores: dict[str, float | None] = {}
        for pillar_name, pillar_factors in PILLARS.items():
            pillar_scores[pillar_name] = calculate_pillar_score(
                factor_scores, pillar_factors
            )

        # Step 3: Calculate preset scores
        preset_scores: dict[str, float] = {}
        for preset_name, preset_weights in PRESETS.items():
            preset_scores[f"score_{preset_name}"] = calculate_flock_score(
                pillar_scores, preset_weights
            )

        results.append({
            "stock_id": stock_id,
            **preset_scores,
            "pillar_profitability": pillar_scores.get("profitability"),
            "pillar_growth": pillar_scores.get("growth"),
            "pillar_health": pillar_scores.get("health"),
            "pillar_valuation": pillar_scores.get("valuation"),
            "pillar_quality": pillar_scores.get("quality"),
        })

    return pd.DataFrame(results)
"""
Description: Flock Score scoring engine — pure math layer. Percentile-rank
normalization, 5-pillar aggregation, 4 preset weight profiles. Maps directly
to quant_models/SKILL.md specification.
"""
