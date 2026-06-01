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
from urllib.parse import urlparse, parse_qs

from app.core.config import settings

# ── Normalise DATABASE_URL ────────────────────────────────
def _asyncpg_url(url: str) -> tuple[str, dict]:
    """
    Rewrite sync PostgreSQL URLs to async, and extract SSL mode.

    Returns: (rewritten_url, connect_args)
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = "postgresql+asyncpg://" + url[len(prefix):]
            break

    # Parse and remove sslmode from query string
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    ssl_mode = query_params.pop("sslmode", [None])[0]

    # Reconstruct URL without sslmode
    if query_params:
        remaining = "&".join(f"{k}={v[0]}" for k, v in query_params.items())
        url = url.split("?")[0] + "?" + remaining
    else:
        url = url.split("?")[0]

    # Build connect_args for asyncpg
    connect_args = {"timeout": 5}
    if ssl_mode:
        # Map psycopg2 ssl modes to asyncpg equivalents
        ssl_map = {
            "require": True,
            "prefer": True,
            "disable": False,
        }
        if ssl_mode in ssl_map:
            connect_args["ssl"] = ssl_map[ssl_mode]

    return url, connect_args

_db_url, _connect_args = _asyncpg_url(settings.DATABASE_URL)

# ── Engine ───────────────────────────────────────────────
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=_connect_args,  # Now includes proper SSL handling
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
