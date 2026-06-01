"""
Configuration management for Social Manager.
Loads all settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import AliasChoices, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # 🎛️ Server 🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️🎛️
    port: int = Field(default=8088, validation_alias=AliasChoices("PORT", "API_PORT"))
    frontend_url: str = Field(default="http://localhost:5173", validation_alias=AliasChoices("FRONTEND_URL", "VITE_FRONTEND_URL"))
    backend_url: str = Field(default="http://localhost:8088", validation_alias=AliasChoices("BACKEND_URL", "API_BASE_URL"))

    # ── Database ──────────────────────────────────────────────────────────────
    social_manager_db_url: str = Field(
        default="sqlite:///./social_manager.db",
        validation_alias=AliasChoices("SOCIAL_MANAGER_DB_URL", "DATABASE_URL"),
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Read from CORS_ORIGINS env var; falls back to localhost defaults
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8088",
        validation_alias="CORS_ORIGINS",
    )

    # ── LLM ───────────────────────────────────────────────────────────────────
    groq_api_key: str | None = None

    # ── Real Feature Integrations ─────────────────────────────────────────────
    openai_api_key: str | None = None
    newsapi_key: str | None = None
    sendgrid_api_key: str | None = None
    email_from: str = "noreply@socialmanager.ai"

    # ── Twilio ────────────────────────────────────────────────────────────────
    twilio_key: str | None = None

    # ── Google ────────────────────────────────────────────────────────────────
    google_client_id: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "YOUTUBE_CLIENT_ID"))
    google_client_secret: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "YOUTUBE_CLIENT_SECRET"))
    google_api_key: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_API_KEY", "YOUTUBE_API_KEY"))

    # ── Twitter / X  (App-level OAuth credentials — kept in .env) ────────────
    twitter_api_key: str | None = None
    twitter_api_secret: str | None = None
    twitter_bearer_token: str | None = None
    # Legacy single-tenant tokens (fallback only; per-user tokens live in DB)
    twitter_access_token: str | None = None
    twitter_access_token_secret: str | None = None

    # ── LinkedIn (App-level OAuth credentials — kept in .env) ─────────────────
    linkedin_client_id: str | None = None
    linkedin_client_secret: str | None = None
    # Legacy single-tenant token (fallback only; per-user tokens live in DB)
    linkedin_access_token: str | None = None

    # ── Meta / Facebook + Instagram (App-level — kept in .env) ───────────────
    facebook_app_id: str | None = None
    facebook_app_secret: str | None = None
    # Legacy single-tenant fallbacks (per-user tokens live in SocialConnection DB)
    facebook_access_token: str | None = None
    facebook_page_id: str | None = None
    instagram_access_token: str | None = None
    instagram_business_account_id: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
        populate_by_name = True

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        local_dev_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8088",
            "http://127.0.0.1:8088",
        ]
        return list(dict.fromkeys([o.strip() for o in self.cors_origins_raw.split(",") if o.strip()] + local_dev_origins))

    @property
    def is_postgres(self) -> bool:
        return self.social_manager_db_url.startswith("postgresql")


settings = Settings()
