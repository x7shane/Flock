"""
Async Database Session Management.

Provides:
  - engine: AsyncEngine connected to PostgreSQL
  - async_session_factory: Creates AsyncSession instances
  - get_db(): FastAPI dependency that yields a session per request
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ── Engine ───────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries when DEBUG=True
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections are alive before using
    connect_args={"timeout": 5},  # Fail fast if DB is unreachable (prevents hangs)
)

# ── Session Factory ──────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── FastAPI Dependency ───────────────────────────────────
async def get_db() -> AsyncSession:
    """
    Yields an async database session for a single request.

    Usage in a route:
        @app.get("/stocks")
        async def get_stocks(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
