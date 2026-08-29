from datetime import datetime, timedelta, timezone
import hashlib
import logging
import secrets
from urllib.parse import urlencode

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.services.auth_service import normalize_email
from app.services.email_service import send_password_reset_email
from app.utils.password import hash_password

logger = logging.getLogger(__name__)
GENERIC_MESSAGE = "If an active account exists for that email, a password reset link has been sent."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def request_password_reset(db: Session, *, email: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    user = db.scalar(select(User).where(func.lower(User.email) == normalize_email(email)))
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
    )
    db.add(reset_token)
    db.flush()

    reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?{urlencode({'token': raw_token})}"
    try:
        send_password_reset_email(recipient=user.email, reset_url=reset_url)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Password reset email delivery failed")
    return GENERIC_MESSAGE


def reset_password(db: Session, *, token: str, new_password: str) -> str:
    now = datetime.now(timezone.utc)
    record = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _hash_token(token),
            PasswordResetToken.used_at.is_(None),
        )
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")

    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        record.used_at = now
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")

    record.user.password_hash = hash_password(new_password)
    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == record.user_id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    db.commit()
    return "Password reset successful. You can now log in."
