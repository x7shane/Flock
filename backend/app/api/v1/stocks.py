"""
Stocks API — list Nifty 200 universe.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
):
    """
    List stocks in the Nifty 200 universe.

    Filters by sector and search term (ticker or company name).
    """
    stocks = NIFTY_200

    if sector:
        stocks = [s for s in stocks if s.sector and s.sector.lower() == sector.lower()]

    if search:
        q = search.lower()
        stocks = [
            s for s in stocks
            if q in s.ticker.lower() or q in s.company_name.lower()
        ]

    total = len(stocks)
    stocks = stocks[offset: offset + limit]

    return [
        StockListItem(
            id=i + offset + 1,
            ticker=s.ticker,
            company_name=s.company_name,
            sector=s.sector,
            industry=s.industry,
        )
        for i, s in enumerate(stocks)
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
