"""
Tests for app.db.session — Session factory and get_db dependency.

These are lightweight unit tests that check our session configuration
without making a real database connection.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class TestSessionFactory:
    """Verify the async_session_factory is properly configured."""

    def test_session_factory_is_async_sessionmaker(self):
        from app.db.session import async_session_factory
        assert isinstance(async_session_factory, async_sessionmaker)

    def test_session_class_is_async_session(self):
        from app.db.session import async_session_factory
        assert async_session_factory.class_ is AsyncSession

    def test_expire_on_commit_is_false(self):
        """expire_on_commit=False is critical for async — prevents lazy loading errors."""
        from app.db.session import async_session_factory
        assert async_session_factory.kw.get("expire_on_commit") is False


class TestEngine:
    """Verify engine is configured with sensible pool settings."""

    def test_engine_pool_pre_ping(self):
        """pool_pre_ping=True ensures stale connections are detected before use."""
        from app.db.session import engine
        assert engine.pool._pre_ping is True

    def test_engine_dialect_is_asyncpg(self):
        from app.db.session import engine
        assert "asyncpg" in engine.dialect.name or "asyncpg" in str(type(engine.dialect))


class TestGetDbDependency:
    """Verify get_db yields a session and rolls back on exception."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """get_db should yield an AsyncSession-compatible object."""
        from app.db.session import get_db

        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("app.db.session.async_session_factory", mock_factory):
            gen = get_db()
            session = await gen.__anext__()
            assert session is mock_session

    @pytest.mark.asyncio
    async def test_get_db_rolls_back_on_exception(self):
        """If an exception is raised inside the dependency, rollback must be called."""
        from app.db.session import get_db

        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_factory = MagicMock(return_value=mock_session)

        with patch("app.db.session.async_session_factory", mock_factory):
            gen = get_db()
            await gen.__anext__()
            try:
                await gen.athrow(ValueError("forced error"))
            except ValueError:
                pass
            mock_session.rollback.assert_called_once()
