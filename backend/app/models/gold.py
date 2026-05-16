"""
Gold price data.

- GoldPrice: Daily gold prices in INR per gram
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GoldPrice(Base):
    """Daily Gold prices (INR per gram)."""

    __tablename__ = "gold_prices"
    __table_args__ = (
        UniqueConstraint("date", name="uq_gold_prices_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    price_per_gram_inr: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<GoldPrice(date={self.date}, price={self.price_per_gram_inr})>"