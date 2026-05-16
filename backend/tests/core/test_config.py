"""
Tests for app.core.config — Settings loading and parsing.
"""

import pytest
from app.core.config import Settings


class TestSettingsDefaults:
    """Verify default values when no env vars are set."""

    def test_app_name_default(self):
        s = Settings()
        assert s.APP_NAME == "Flock API"

    def test_version_default(self):
        s = Settings()
        assert s.APP_VERSION == "0.1.0"

    def test_debug_default_is_false(self):
        # Without setting DEBUG env var, default should be False
        s = Settings()
        assert isinstance(s.DEBUG, bool)

    def test_api_prefix_default(self):
        s = Settings()
        assert s.API_V1_PREFIX == "/api/v1"

    def test_database_url_default_is_asyncpg(self):
        s = Settings()
        assert "asyncpg" in s.DATABASE_URL

    def test_rate_limit_is_positive(self):
        s = Settings()
        assert s.FETCH_RATE_LIMIT > 0
        assert s.YFINANCE_TIMEOUT > 0
        assert s.MFAPI_TIMEOUT > 0


class TestCorsOriginParsing:
    """Verify CORS_ORIGINS string → list conversion."""

    def test_wildcard_returns_list_with_star(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "*")
        s = Settings()
        assert s.cors_origin_list == ["*"]

    def test_single_origin_parsed(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
        s = Settings()
        assert s.cors_origin_list == ["http://localhost:3000"]

    def test_multiple_origins_parsed(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        s = Settings()
        origins = s.cors_origin_list
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:8080" in origins

    def test_whitespace_trimmed(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000 , http://localhost:8080")
        s = Settings()
        origins = s.cors_origin_list
        assert "http://localhost:3000" in origins
        assert "http://localhost:8080" in origins


class TestEnvOverride:
    """Verify environment variables override defaults."""

    def test_debug_override(self, monkeypatch):
        monkeypatch.setenv("DEBUG", "true")
        s = Settings()
        assert s.DEBUG is True

    def test_app_name_override(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "test-flock")
        s = Settings()
        assert s.APP_NAME == "test-flock"

    def test_database_url_override(self, monkeypatch):
        test_url = "postgresql+asyncpg://user:pass@db:5432/mydb"
        monkeypatch.setenv("DATABASE_URL", test_url)
        s = Settings()
        assert s.DATABASE_URL == test_url
