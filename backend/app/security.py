from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.config import get_settings


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret:
        raise RuntimeError("JWT_SECRET is required for authentication operations")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 bytes; use a cryptographically random value")
    return secret


def access_token_lifetime_seconds() -> int:
    # Never allow an inherited 90-day deployment setting to produce a long JWT.
    return max(60, min(get_settings().access_token_expire_minutes, 15) * 60)


def _jwt_algorithm() -> str:
    if get_settings().jwt_algorithm != "HS256":
        raise RuntimeError("JWT_ALGORITHM must be HS256 for this shared-secret deployment")
    return "HS256"


def create_access_token(*, user_id: int, session_id: str | None = None, auth_version: int = 0) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=access_token_lifetime_seconds()),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "av": auth_version,
    }
    if session_id is not None:
        payload["sid"] = session_id
    return jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())


def decode_access_claims(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, _jwt_secret(), algorithms=[_jwt_algorithm()],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            options={"require": ["sub", "iat", "exp", "iss", "aud", "av"]},
        )
        subject = payload.get("sub")
        version = payload.get("av")
        if not isinstance(subject, str) or not subject.isdecimal() or int(subject) <= 0:
            raise InvalidTokenError("Invalid token subject")
        if type(version) is not int or version < 0:
            raise InvalidTokenError("Invalid authentication version")
        return payload
    except (InvalidTokenError, TypeError, ValueError) as exc:
        raise InvalidTokenError("Invalid access token") from exc


def decode_access_token(token: str) -> int:
    """Compatibility helper for callers inspecting subject, not authorization."""
    return int(decode_access_claims(token)["sub"])
