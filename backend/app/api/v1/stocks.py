"""
Stocks API — list Nifty 200 universe.
"""

from fastapi import APIRouter

from app.data.nifty200 import NIFTY_200
from app.schemas.scores import StockListItem

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
