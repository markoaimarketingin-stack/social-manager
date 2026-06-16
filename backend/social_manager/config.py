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
    groq_api_key: str | None = Field(default=None, validation_alias=AliasChoices("GROQ_API_KEY"))

    # ── Real Feature Integrations ─────────────────────────────────────────────
    openai_api_key: str | None = Field(default=None, validation_alias=AliasChoices("OPENAI_API_KEY"))
    newsapi_key: str | None = Field(default=None, validation_alias=AliasChoices("NEWSAPI_KEY"))
    sendgrid_api_key: str | None = Field(default=None, validation_alias=AliasChoices("SENDGRID_API_KEY"))
    email_from: str = Field(default="noreply@socialmanager.ai", validation_alias=AliasChoices("EMAIL_FROM"))

    # ── Twilio ────────────────────────────────────────────────────────────────
    twilio_key: str | None = Field(default=None, validation_alias=AliasChoices("TWILIO_KEY"))

    # ── Google ────────────────────────────────────────────────────────────────
    google_client_id: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "YOUTUBE_CLIENT_ID"))
    google_client_secret: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "YOUTUBE_CLIENT_SECRET"))
    google_api_key: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_API_KEY", "YOUTUBE_API_KEY"))

    # ── Twitter / X  (App-level OAuth credentials — kept in .env) ────────────
    twitter_api_key: str | None = Field(default=None, validation_alias=AliasChoices("TWITTER_API_KEY"))
    twitter_api_secret: str | None = Field(default=None, validation_alias=AliasChoices("TWITTER_API_SECRET"))
    twitter_bearer_token: str | None = Field(default=None, validation_alias=AliasChoices("TWITTER_BEARER_TOKEN"))
    # Legacy single-tenant tokens (fallback only; per-user tokens live in DB)
    twitter_access_token: str | None = Field(default=None, validation_alias=AliasChoices("TWITTER_ACCESS_TOKEN"))
    twitter_access_token_secret: str | None = Field(default=None, validation_alias=AliasChoices("TWITTER_ACCESS_TOKEN_SECRET"))

    # ── LinkedIn (App-level OAuth credentials — kept in .env) ─────────────────
    linkedin_client_id: str | None = Field(default=None, validation_alias=AliasChoices("LINKEDIN_CLIENT_ID"))
    linkedin_client_secret: str | None = Field(default=None, validation_alias=AliasChoices("LINKEDIN_CLIENT_SECRET"))
    # Legacy single-tenant token (fallback only; per-user tokens live in DB)
    linkedin_access_token: str | None = Field(default=None, validation_alias=AliasChoices("LINKEDIN_ACCESS_TOKEN"))

    # ── Meta / Facebook + Instagram (App-level — kept in .env) ───────────────
    facebook_app_id: str | None = Field(default=None, validation_alias=AliasChoices("FACEBOOK_APP_ID"))
    facebook_app_secret: str | None = Field(default=None, validation_alias=AliasChoices("FACEBOOK_APP_SECRET"))
    # Legacy single-tenant fallbacks (per-user tokens live in SocialConnection DB)
    facebook_access_token: str | None = Field(default=None, validation_alias=AliasChoices("FACEBOOK_ACCESS_TOKEN"))
    facebook_page_id: str | None = Field(default=None, validation_alias=AliasChoices("FACEBOOK_PAGE_ID"))
    instagram_access_token: str | None = Field(default=None, validation_alias=AliasChoices("INSTAGRAM_ACCESS_TOKEN"))
    instagram_business_account_id: str | None = Field(default=None, validation_alias=AliasChoices("INSTAGRAM_BUSINESS_ACCOUNT_ID"))

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
