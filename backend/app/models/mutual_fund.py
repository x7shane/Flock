"""
Mutual Fund entity and NAV data.

- MutualFund: Curated list of index funds
- MfNav: Daily NAV history
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    pass  # No circular imports needed


class MutualFund(Base):
    """Curated list of Index Funds."""

    __tablename__ = "mutual_funds"

    id: Mapped[int] = mapped_column(primary_key=True)
    scheme_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "Nifty 50 Index"
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    navs: Mapped[list["MfNav"]] = relationship(back_populates="fund", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<MutualFund(scheme_code={self.scheme_code}, name={self.scheme_name})>"


class MfNav(Base):
    """Daily NAV data for mutual funds."""

    __tablename__ = "mf_navs"
    __table_args__ = (
        UniqueConstraint("fund_id", "date", name="uq_mf_navs_fund_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("mutual_funds.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    nav: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    # Relationships
    fund: Mapped["MutualFund"] = relationship(back_populates="navs")

    def __repr__(self) -> str:
        return f"<MfNav(fund_id={self.fund_id}, date={self.date}, nav={self.nav})>"