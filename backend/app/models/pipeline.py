"""
Pipeline run audit log.

- PipelineRun: Logs data pipeline job executions
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PipelineRun(Base):
    """Audit log for data pipeline executions."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'prices', 'fundamentals', 'scores', etc.
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # 'running', 'completed', 'failed', 'partial'
    tickers_total: Mapped[Optional[int]] = mapped_column(Integer)
    tickers_success: Mapped[Optional[int]] = mapped_column(Integer)
    tickers_failed: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<PipelineRun(id={self.id}, type={self.run_type}, status={self.status})>"