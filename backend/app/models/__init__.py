"""
SQLAlchemy ORM Models.

All models are imported here so Alembic can autodetect them.
Import this file in env.py: `from app.models import Base`
"""

from app.models.gold import GoldPrice
from app.models.mutual_fund import MfNav, MutualFund
from app.models.pipeline import PipelineRun
from app.models.stock import FlockScore, Fundamental, Stock, StockPrice

# Re-export Base for convenience
from app.db.base import Base

__all__ = [
    "Base",
    "Stock",
    "StockPrice",
    "Fundamental",
    "FlockScore",
    "MutualFund",
    "MfNav",
    "GoldPrice",
    "PipelineRun",
]