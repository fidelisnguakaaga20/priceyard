from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.auth_schema import TokenResponse
from app.security import access_token_lifetime_seconds, create_access_token


def utc_aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def hash_credential(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def invalid_session() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _token_response(user: User, session: AuthSession, raw_refresh: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id=user.id, session_id=session.id, auth_version=user.auth_version),
        refresh_token=raw_refresh, expires_in=access_token_lifetime_seconds(),
        session_expires_at=utc_aware(session.expires_at),
    )


def issue_session(db: Session, user: User, *, remember_me: bool = True) -> TokenResponse:
    # User-first locking serializes issuance with reset and account disabling.
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if user is None or not user.is_active:
        raise invalid_session()
    settings = get_settings()
    now = datetime.now(timezone.utc)
    lifetime = (
        timedelta(days=settings.auth_session_remember_days)
        if remember_me else timedelta(hours=settings.auth_session_nonremember_hours)
    )
    raw_refresh = secrets.token_urlsafe(48)
    session = AuthSession(
        id=str(uuid.uuid4()), user_id=user.id, refresh_token_hash=hash_credential(raw_refresh),
        expires_at=now + lifetime, last_refreshed_at=now,
    )
    db.add(session)
    db.flush()
    return _token_response(user, session, raw_refresh)


def refresh_session(db: Session, *, refresh_token: str) -> TokenResponse:
    credential_hash = hash_credential(refresh_token)
    owner_id = db.scalar(select(AuthSession.user_id).where(AuthSession.refresh_token_hash == credential_hash))
    if owner_id is None:
        raise invalid_session()
    # Always lock user before session to avoid reset/logout-all deadlocks.
    user = db.scalar(select(User).where(User.id == owner_id).with_for_update().execution_options(populate_existing=True))
    session = db.scalar(
        select(AuthSession).where(AuthSession.refresh_token_hash == credential_hash)
        .with_for_update().execution_options(populate_existing=True)
    )
    now = datetime.now(timezone.utc)
    if user is None or not user.is_active or session is None or session.revoked_at is not None:
        raise invalid_session()
    if utc_aware(session.expires_at) <= now:
        raise invalid_session()
    raw_refresh = secrets.token_urlsafe(48)
    session.refresh_token_hash = hash_credential(raw_refresh)
    session.last_refreshed_at = now
    db.flush()
    return _token_response(user, session, raw_refresh)


def revoke_sessions(db: Session, user: User, *, now: datetime | None = None) -> None:
    """Caller holds the user lock; all changes share the caller's transaction."""
    timestamp = now or datetime.now(timezone.utc)
    user.auth_version = (user.auth_version or 0) + 1
    db.execute(update(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).values(revoked_at=timestamp))
    db.flush()


def logout_session(db: Session, *, user_id: int, session_id: str) -> None:
    now = datetime.now(timezone.utc)
    db.execute(update(AuthSession).where(
        AuthSession.id == session_id, AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None),
    ).values(revoked_at=now))
    db.flush()


def logout_all_sessions(db: Session, user: User) -> None:
    locked = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if locked is None:
        raise invalid_session()
    revoke_sessions(db, locked)
