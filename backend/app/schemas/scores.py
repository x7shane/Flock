"""
Pydantic schemas for Flock Score API responses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PillarScores(BaseModel):
    """Pillar-level score breakdown."""
    profitability: float | None = Field(None, description="Profitability pillar (0-100)")
    growth: float | None = Field(None, description="Growth pillar (0-100)")
    health: float | None = Field(None, description="Financial health pillar (0-100)")
    valuation: float | None = Field(None, description="Valuation pillar (0-100)")
    quality: float | None = Field(None, description="Quality pillar (0-100)")


class FlockScoreResponse(BaseModel):
    """Flock Score for a single stock."""
    stock_id: int
    ticker: str
    company_name: str
    sector: str | None = None
    score_balanced: float | None = None
    score_growth: float | None = None
    score_value: float | None = None
    score_conservative: float | None = None
    pillars: PillarScores = PillarScores()


class StockListItem(BaseModel):
    """Lightweight stock info for listing."""
    id: int
    ticker: str
    company_name: str
    sector: str | None = None
    industry: str | None = None
    is_active: bool = True
    flock_score: float | None = Field(None, description="Flock balanced score (0-100), None if not yet computed")


class FundamentalsResponse(BaseModel):
    """Current fundamental factors for a stock — all 16 Flock factors."""

    stock_id: int
    ticker: str
    company_name: str
    sector: str | None = None

    # ── Profitability ───────────────────────────────────────
    roe: float | None = Field(None, description="Return on Equity (%)")
    roce: float | None = Field(None, description="Return on Capital Employed (%)")
    net_profit_margin: float | None = Field(None, description="Net Profit Margin (%)")

    # ── Growth ──────────────────────────────────────────────
    revenue_cagr_3yr: float | None = Field(None, description="3-Year Revenue CAGR (%)")
    eps_growth_3yr: float | None = Field(None, description="3-Year EPS Growth (%)")

    # ── Financial Health ────────────────────────────────────
    debt_equity: float | None = Field(None, description="Debt to Equity ratio")
    current_ratio: float | None = Field(None, description="Current Ratio")
    interest_coverage: float | None = Field(None, description="Interest Coverage Ratio")
    free_cash_flow: float | None = Field(None, description="Free Cash Flow (INR Cr)")

    # ── Valuation ───────────────────────────────────────────
    pe_ratio: float | None = Field(None, description="Price to Earnings")
    pb_ratio: float | None = Field(None, description="Price to Book")
    peg_ratio: float | None = Field(None, description="PEG Ratio")
    dividend_yield: float | None = Field(None, description="Dividend Yield (%)")

    # ── Quality ─────────────────────────────────────────────
    promoter_holding_pct: float | None = Field(None, description="Promoter Holding (%)")
    promoter_pledge_pct: float | None = Field(None, description="Promoter Pledge (%)")
    fii_dii_trend: float | None = Field(None, description="FII/DII net buy trend")

    # ── Metadata ────────────────────────────────────────────
    market_cap: float | None = Field(None, description="Market Cap (INR Cr)")
    fetched_at: str | None = Field(None, description="Data freshness timestamp (ISO)")
