from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or backend/.env."""

    app_name: str = "PriceYard API"
    app_env: str = "development"
    debug: bool = False
    database_url: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    google_client_id: str | None = None
    access_token_expire_minutes: int = 129_600  # 90 days -- users stay logged in until they explicitly log out
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
    vapid_public_key: str | None = None
    vapid_private_key: str | None = None
    vapid_claim_email: str = "fidelisnguakaaga20@gmail.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
