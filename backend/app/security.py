from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from app.config import get_settings


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret:
        raise RuntimeError("JWT_SECRET is required for authentication operations")
    return secret


def create_access_token(*, user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int:
    settings = get_settings()
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise InvalidTokenError("Missing token subject")
        return int(subject)
    except (InvalidTokenError, TypeError, ValueError) as exc:
        raise InvalidTokenError("Invalid access token") from exc
