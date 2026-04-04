"""
Flock Application Configuration.

Loads settings from environment variables (via .env file).
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Flock API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ─────────────────────────────────────────
    # Default matches docker-compose.yml credentials
    DATABASE_URL: str = "postgresql+asyncpg://flock:flock_password@localhost:5432/flock_db"

    # ── CORS ─────────────────────────────────────────────
    # Comma-separated origins, e.g. "http://localhost:3000,http://localhost:8080"
    CORS_ORIGINS: str = "*"

    # ── Data Pipeline ────────────────────────────────────
    YFINANCE_TIMEOUT: int = 30
    MFAPI_TIMEOUT: int = 15
    FETCH_RATE_LIMIT: float = 2.0  # calls per second

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Singleton — import this everywhere
settings = Settings()
