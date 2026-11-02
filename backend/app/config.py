"""
app/config.py — Application Configuration

Defines configuration settings for the backend application, loaded from
environment variables with sensible defaults.
"""

from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings class.
    Reads from .env file when running locally.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── Database Config ──────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_eval_db",
        alias="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # ── Security & Operational Config ───────────────────────────────────────────
    environment: str = Field(default="development", alias="ENVIRONMENT")
    allowed_hosts: list[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    jwt_secret_key: str = Field(default="dev_secret_key_change_me_in_production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Upload Rate Limiting Config (In-memory)
    rate_limit_upload_limit: int = Field(default=10, alias="RATE_LIMIT_UPLOAD_LIMIT")
    rate_limit_upload_window: int = Field(default=60, alias="RATE_LIMIT_UPLOAD_WINDOW")

    # ── File Storage Config ──────────────────────────────────────────────────────
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    max_upload_size_bytes: int = Field(default=52428800, alias="MAX_UPLOAD_SIZE_BYTES")  # 50MB default

    # ClamAV Configuration
    clamav_enabled: bool = Field(default=False, alias="CLAMAV_ENABLED")
    clamav_host: str = Field(default="localhost", alias="CLAMAV_HOST")
    clamav_port: int = Field(default=3310, alias="CLAMAV_PORT")
    clamav_fail_closed: bool = Field(default=True, alias="CLAMAV_FAIL_CLOSED")


    # ── OCR & AI Models Config ───────────────────────────────────────────────────
    ocr_confidence_threshold: float = Field(default=0.6, alias="OCR_CONFIDENCE_THRESHOLD")
    sentence_transformer_model: str = Field(
        default="paraphrase-multilingual-mpnet-base-v2",
        alias="SENTENCE_TRANSFORMER_MODEL"
    )

    # ── Redis Config ──────────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton-like)."""
    return Settings()
