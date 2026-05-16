"""
Stock entity and related models.

- Stock: Universe of Indian equities (Nifty 200)
- StockPrice: Daily OHLCV data
- Fundamental: 16 factors for Flock Score
- FlockScore: Pre-computed scores
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Index, Numeric, String, Text, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.mutual_fund import MutualFund
    from app.models.pipeline import PipelineRun


class Stock(Base):
    """Universe of Indian equities (Nifty 200)."""

    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[Optional[str]] = mapped_column(String(100))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    prices: Mapped[list["StockPrice"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    fundamentals: Mapped[list["Fundamental"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    flock_scores: Mapped[list["FlockScore"]] = relationship(back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Stock(ticker={self.ticker}, name={self.company_name})>"


class StockPrice(Base):
    """Daily OHLCV data for stocks."""

    __tablename__ = "stock_prices"
    __table_args__ = (
        UniqueConstraint("stock_id", "date", name="uq_stock_prices_stock_date"),
        Index("ix_stock_prices_stock_date_desc", "stock_id", "date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    high: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    low: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    close: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    adj_close: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    volume: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Relationships
    stock: Mapped["Stock"] = relationship(back_populates="prices")

    def __repr__(self) -> str:
        return f"<StockPrice(stock_id={self.stock_id}, date={self.date}, close={self.close})>"


class Fundamental(Base):
    """
    Fundamental factors for a stock (16 factors for Flock Score).
    SCD2: Tracks historical changes with valid_from/valid_to.
    """

    __tablename__ = "fundamentals"
    __table_args__ = (
        UniqueConstraint("stock_id", "valid_from", name="uq_fundamentals_stock_valid_from"),
        Index("ix_fundamentals_current", "stock_id", "is_current"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)

    # SCD2 tracking
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Profitability factors
    roe: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # Return on Equity
    roce: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # Return on Capital Employed
    net_profit_margin: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # Net Profit Margin

    # Growth factors
    revenue_cagr_3yr: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # 3-year Revenue CAGR
    eps_growth_3yr: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # 3-year EPS Growth

    # Health factors
    debt_equity: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))  # Debt to Equity Ratio
    current_ratio: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # Current Ratio
    interest_coverage: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))  # Interest Coverage Ratio
    free_cash_flow: Mapped[Optional[float]] = mapped_column(Numeric(20, 4))  # Free Cash Flow (absolute value)

    # Valuation factors
    pe_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))  # Price to Earnings
    pb_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))  # Price to Book
    peg_ratio: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # PEG Ratio
    dividend_yield: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))  # Dividend Yield

    # Quality factors
    promoter_holding_pct: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))  # Promoter Holding %
    promoter_pledge_pct: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))  # Promoter Pledge %
    fii_dii_trend: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))  # FII/DII trend indicator

    # Metadata
    market_cap: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))  # Market cap in INR
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    stock: Mapped["Stock"] = relationship(back_populates="fundamentals")

    def __repr__(self) -> str:
        return f"<Fundamental(stock_id={self.stock_id}, pe={self.pe_ratio}, current={self.is_current})>"


class FlockScore(Base):
    """
    Pre-computed Flock Scores for a stock.
    SCD2: Tracks historical changes with valid_from/valid_to.
    """

    __tablename__ = "flock_scores"
    __table_args__ = (
        UniqueConstraint("stock_id", "valid_from", name="uq_flock_scores_stock_valid_from"),
        Index("ix_flock_scores_current", "stock_id", "is_current"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)

    # SCD2 tracking
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Preset scores (0-100)
    score_balanced: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    score_growth: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    score_value: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    score_conservative: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Pillar scores (0-100)
    pillar_profitability: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    pillar_growth: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    pillar_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    pillar_valuation: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    pillar_quality: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Metadata
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    stock: Mapped["Stock"] = relationship(back_populates="flock_scores")

    def __repr__(self) -> str:
        return f"<FlockScore(stock_id={self.stock_id}, balanced={self.score_balanced}, current={self.is_current})>"