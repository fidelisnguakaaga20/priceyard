from datetime import datetime, timedelta, timezone
import secrets

import jwt
from jwt import InvalidTokenError

from app.config import get_settings


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret:
        raise RuntimeError("JWT_SECRET is required for authentication operations")
    return secret


def create_access_token(*, user_id: int, auth_version: int = 0) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "auth_version": auth_version,
        "jti": secrets.token_urlsafe(24),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_access_claims(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[settings.jwt_algorithm], options={"require": ["sub", "iat", "exp"]})
        subject = payload.get("sub")
        if subject is None:
            raise InvalidTokenError("Missing token subject")
        if int(subject) <= 0 or type(payload.get("auth_version", 0)) is not int or payload.get("auth_version", 0) < 0:
            raise InvalidTokenError("Invalid token identity/version")
        return payload
    except (InvalidTokenError, TypeError, ValueError) as exc:
        raise InvalidTokenError("Invalid access token") from exc


def decode_access_token(token: str) -> int:
    return int(decode_access_claims(token)["sub"])
