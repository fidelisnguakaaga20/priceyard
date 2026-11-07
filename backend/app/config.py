from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or backend/.env."""

    app_name: str = "PriceYard API"
    app_env: str = "development"
    debug: bool = False
    # Developer API pages (/docs, /redoc, /openapi.json) stay off unless explicitly enabled,
    # e.g. API_DOCS_ENABLED=true in a local backend/.env. Never enable on the live server.
    api_docs_enabled: bool = False
    # Error alerts (audit item 10). Empty = off. Set SENTRY_DSN on the live server only.
    sentry_dsn: str | None = None
    database_url: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    google_client_id: str | None = None
    # Protected existing founder account; never a public registration grant.
    owner_email: str = "fidelisnguakaaga20@gmail.com"
    access_token_expire_minutes: int = 129_600  # 90 days -- users stay logged in until they explicitly log out
    # Admin logins are shorter (owner-approved audit item 12): a lost or stolen admin
    # device stops working within 7 days. Also enforced for older admin logins.
    admin_access_token_expire_minutes: int = 10_080  # 7 days
    cors_origins: str = ""
    frontend_url: str = "http://127.0.0.1:5173"
    password_reset_expire_minutes: int = 15
    password_reset_cooldown_seconds: int = 60
    brevo_api_key: str | None = None
    brevo_api_url: str = "https://api.brevo.com/v3/smtp/email"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "PriceYard"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    paystack_secret_key: str | None = None
    paystack_public_key: str | None = None
    cron_secret: str | None = None
    ops_recovery_enabled: bool = False
    vapid_public_key: str | None = None
    vapid_private_key: str | None = None
    vapid_claim_email: str = "fidelisnguakaaga20@gmail.com"
    whatsapp_phone_number_id: str | None = None
    whatsapp_access_token: str | None = None
    whatsapp_api_version: str = "v21.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
