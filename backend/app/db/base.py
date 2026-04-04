"""
SQLAlchemy Declarative Base.

All ORM models inherit from this Base class.
Import this in every model file:
    from app.db.base import Base
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in Flock."""
    pass
