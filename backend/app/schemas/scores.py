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
