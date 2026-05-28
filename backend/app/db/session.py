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

# ── Normalise DATABASE_URL ────────────────────────────────
# Neon, Heroku, and many CI secrets store the URL as
# "postgresql://" or "postgres://" which SQLAlchemy maps to
# psycopg2 (sync).  We always need "postgresql+asyncpg://"
# for the async engine — rewrite it here so the secret works
# in any format.
def _asyncpg_url(url: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url  # already has +asyncpg or custom scheme

_db_url = _asyncpg_url(settings.DATABASE_URL)

# ── Engine ───────────────────────────────────────────────
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,  # Log SQL queries when DEBUG=True
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections are alive before using
    connect_args={"timeout": 5},  # Fail fast if DB is unreachable
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
