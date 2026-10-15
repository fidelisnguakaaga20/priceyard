from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from urllib.parse import urlencode

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.services.auth_service import normalize_email
from app.services.auth_session_service import revoke_sessions
from app.services.notification_service import enqueue_secure_email
from app.utils.password import hash_password

GENERIC_MESSAGE = "If an active account exists for that email, a password reset link has been sent."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def request_password_reset(db: Session, *, email: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    user = db.scalar(select(User).where(func.lower(User.email) == normalize_email(email)).with_for_update())
    if user is None or not user.is_active:
        return GENERIC_MESSAGE

    latest = db.scalar(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.created_at.desc())
        .limit(1)
    )
    if latest is not None:
        created_at = latest.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if created_at > now - timedelta(seconds=settings.password_reset_cooldown_seconds):
            return GENERIC_MESSAGE

    raw_token = secrets.token_urlsafe(48)
    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=now + timedelta(minutes=settings.password_reset_expire_minutes),
        created_at=now,
    )
    db.add(reset_token)
    db.flush()

    reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?{urlencode({'token': raw_token})}"
    enqueue_secure_email(
        db, recipient=user.email, subject="Reset your PriceYard password",
        body=f"Open this secure link within {settings.password_reset_expire_minutes} minutes:\n{reset_url}\n\nIf you did not request this, ignore this email.",
        expires_at=reset_token.expires_at, user_id=user.id, event_key=f"password-reset:{reset_token.id}",
        proof_type="password_reset", proof_id=reset_token.id,
    )
    return GENERIC_MESSAGE


def reset_password(db: Session, *, token: str, new_password: str) -> str:
    now = datetime.now(timezone.utc)
    try:
        password_hash = hash_password(new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    token_hash = _hash_token(token)
    owner_id = db.scalar(select(PasswordResetToken.user_id).where(PasswordResetToken.token_hash == token_hash))
    if owner_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")
    user = db.scalar(select(User).where(User.id == owner_id).with_for_update().execution_options(populate_existing=True))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")
    # Conditional UPDATE is the one-use claim, not an earlier Python check.
    claimed_user = db.scalar(update(PasswordResetToken).where(
        PasswordResetToken.token_hash == token_hash, PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now,
    ).values(used_at=now).returning(PasswordResetToken.user_id).execution_options(synchronize_session="fetch"))
    if claimed_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")
    user.password_hash = password_hash
    user.email_verified = True  # Delivery of a valid secret proves email ownership.
    if user.auth_provider == "google":
        user.auth_provider = "local_google"
    revoke_sessions(db, user, now=now)
    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    db.flush()
    return "Password reset successful. Previous sessions have been signed out. You can now log in."
