"""
Stocks API — list Nifty 200 universe with Flock Scores.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.data.nifty200 import NIFTY_200
from app.db.session import get_db
from app.models.stock import FlockScore, Fundamental, Stock
from app.schemas.scores import FlockScoreResponse, FundamentalsResponse, PillarScores, StockListItem

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("", response_model=list[StockListItem])
async def list_stocks(
    sector: str | None = None,
    search: str | None = None,
    limit: int = 200,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """
    List stocks in the Nifty 200 universe with their current Flock Score.

    Reads from the database and joins with flock_scores (is_current=True)
    to include the balanced score. Filters by sector and search term.
    """
    # Build query: stocks LEFT JOIN current flock_scores
    CurrentScore = aliased(FlockScore)

    query = (
        select(
            Stock.id,
            Stock.ticker,
            Stock.company_name,
            Stock.sector,
            Stock.industry,
            Stock.is_active,
            CurrentScore.score_balanced,
            CurrentScore.pillar_profitability,
            CurrentScore.pillar_growth,
            CurrentScore.pillar_health,
            CurrentScore.pillar_valuation,
            CurrentScore.pillar_quality,
        )
        .outerjoin(
            CurrentScore,
            (CurrentScore.stock_id == Stock.id) & (CurrentScore.is_current == True),  # noqa: E712
        )
        .where(Stock.is_active == True)  # noqa: E712
        .order_by(Stock.id)
    )

    # Apply filters
    if sector:
        query = query.where(func.lower(Stock.sector) == sector.lower())

    if search:
        q = f"%{search.lower()}%"
        query = query.where(
            func.lower(Stock.ticker).like(q) | func.lower(Stock.company_name).like(q)
        )

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    rows = result.all()

    return [
        StockListItem(
            id=row.id,
            ticker=row.ticker,
            company_name=row.company_name,
            sector=row.sector,
            industry=row.industry,
            is_active=row.is_active,
            flock_score=round(float(row.score_balanced), 1) if row.score_balanced is not None else None,
            pillar_profitability=round(float(row.pillar_profitability), 1) if row.pillar_profitability is not None else None,
            pillar_growth=round(float(row.pillar_growth), 1) if row.pillar_growth is not None else None,
            pillar_health=round(float(row.pillar_health), 1) if row.pillar_health is not None else None,
            pillar_valuation=round(float(row.pillar_valuation), 1) if row.pillar_valuation is not None else None,
            pillar_quality=round(float(row.pillar_quality), 1) if row.pillar_quality is not None else None,
        )
        for row in rows
    ]


@router.get("/sectors")
async def list_sectors():
    """List all unique sectors in the universe."""
    sectors = sorted({s.sector for s in NIFTY_200 if s.sector})
    return {"sectors": sectors}


@router.get("/{ticker}/fundamentals", response_model=FundamentalsResponse)
async def get_stock_fundamentals(ticker: str, session: AsyncSession = Depends(get_db)):
    """
    Get current fundamental data for a single stock.

    Returns all 16 raw factor values (ROE, PE, D/E etc.) from the latest
    SCD2 snapshot. Returns 404 if the pipeline has not yet fetched data.
    """
    result = await session.execute(select(Stock).where(Stock.ticker == ticker.upper()))
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")

    result = await session.execute(
        select(Fundamental)
        .where(Fundamental.stock_id == stock.id)
        .where(Fundamental.is_current.is_(True))
    )
    fund = result.scalar_one_or_none()

    if not fund:
        raise HTTPException(
            status_code=404,
            detail=f"No fundamental data available for {ticker}. Run the data pipeline first."
        )

    def _f(v) -> float | None:
        return float(v) if v is not None else None

    return FundamentalsResponse(
        stock_id=stock.id,
        ticker=stock.ticker,
        company_name=stock.company_name,
        sector=stock.sector,
        roe=_f(fund.roe),
        roce=_f(fund.roce),
        net_profit_margin=_f(fund.net_profit_margin),
        revenue_cagr_3yr=_f(fund.revenue_cagr_3yr),
        eps_growth_3yr=_f(fund.eps_growth_3yr),
        debt_equity=_f(fund.debt_equity),
        current_ratio=_f(fund.current_ratio),
        interest_coverage=_f(fund.interest_coverage),
        free_cash_flow=_f(fund.free_cash_flow),
        pe_ratio=_f(fund.pe_ratio),
        pb_ratio=_f(fund.pb_ratio),
        peg_ratio=_f(fund.peg_ratio),
        dividend_yield=_f(fund.dividend_yield),
        promoter_holding_pct=_f(fund.promoter_holding_pct),
        promoter_pledge_pct=_f(fund.promoter_pledge_pct),
        fii_dii_trend=_f(fund.fii_dii_trend),
        market_cap=_f(fund.market_cap),
        fetched_at=fund.fetched_at.isoformat() if fund.fetched_at else None,
    )


@router.get("/{ticker}/score", response_model=FlockScoreResponse)
async def get_stock_score(ticker: str, session: AsyncSession = Depends(get_db)):
    """
    Get Flock score breakdown for a single stock.

    Returns the current score with all preset scores and pillar breakdowns.
    """
    # Find stock by ticker
    result = await session.execute(select(Stock).where(Stock.ticker == ticker.upper()))
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")

    # Find current flock score
    result = await session.execute(
        select(FlockScore)
        .where(FlockScore.stock_id == stock.id)
        .where(FlockScore.is_current.is_(True))
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(status_code=404, detail=f"No Flock score available for {ticker}")

    return FlockScoreResponse(
        stock_id=stock.id,
        ticker=stock.ticker,
        company_name=stock.company_name,
        sector=stock.sector,
        score_balanced=float(score.score_balanced) if score.score_balanced is not None else None,
        score_growth=float(score.score_growth) if score.score_growth is not None else None,
        score_value=float(score.score_value) if score.score_value is not None else None,
        score_conservative=float(score.score_conservative) if score.score_conservative is not None else None,
        pillars=PillarScores(
            profitability=float(score.pillar_profitability) if score.pillar_profitability is not None else None,
            growth=float(score.pillar_growth) if score.pillar_growth is not None else None,
            health=float(score.pillar_health) if score.pillar_health is not None else None,
            valuation=float(score.pillar_valuation) if score.pillar_valuation is not None else None,
            quality=float(score.pillar_quality) if score.pillar_quality is not None else None,
        ),
    )
