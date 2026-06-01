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
from urllib.parse import urlparse, parse_qs, urlunparse

from app.core.config import settings

# ── Normalise DATABASE_URL ────────────────────────────────
def _asyncpg_url(url: str) -> tuple[str, dict]:
    """
    Rewrite sync PostgreSQL URLs to async, stripping all incompatible query params.
    asyncpg doesn't accept psycopg2-specific params like sslmode or channel_binding.

    Returns: (rewritten_url_without_params, connect_args)
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = "postgresql+asyncpg://" + url[len(prefix):]
            break

    # Parse URL to extract and remove ALL query parameters
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    # Extract SSL mode before wiping params
    ssl_mode = query_params.pop("sslmode", [None])[0]

    # Rebuild URL with NO query string — asyncpg doesn't accept any
    # psycopg2-style params (sslmode, channel_binding, options, etc.)
    url_clean = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        "",               # ← strip entire query string
        parsed.fragment,
    ))

    # Build connect_args for asyncpg
    connect_args: dict = {"timeout": 5}
    ssl_map = {"require": True, "prefer": True, "disable": False}
    if ssl_mode and ssl_mode in ssl_map:
        connect_args["ssl"] = ssl_map[ssl_mode]

    return url_clean, connect_args


_db_url, _connect_args = _asyncpg_url(settings.DATABASE_URL)

# ── Engine ───────────────────────────────────────────────
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=_connect_args,
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
