from functools import lru_cache
import os

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
    access_token_expire_minutes: int = 15
    auth_session_remember_days: int = 90
    auth_session_nonremember_hours: int = 24
    jwt_issuer: str = "priceyard"
    jwt_audience: str = "priceyard-api"
    email_verification_expire_minutes: int = 30
    email_verification_cooldown_seconds: int = 60
    rate_limit_storage_uri: str = "memory://"
    notification_max_attempts: int = 5
    max_request_bytes: int = 3 * 1024 * 1024
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
    # The isolated runner sets this before any application import. Never load a
    # developer/production dotenv file from a test process.
    if os.environ.get("PRICEYARD_TEST_MODE") == "isolated":
        return Settings(_env_file=None)
    return Settings()
