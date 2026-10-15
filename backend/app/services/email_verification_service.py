from datetime import datetime, timedelta, timezone
import secrets
from urllib.parse import urlencode

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User
from app.services.auth_service import normalize_email
from app.services.auth_session_service import hash_credential, utc_aware
from app.services.notification_service import enqueue_secure_email

GENERIC_VERIFICATION_MESSAGE = "If an eligible account uses that email, a verification link has been sent."


def request_email_verification(db: Session, *, email: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    # The account lock prevents simultaneous resend requests bypassing cooldown.
    user = db.scalar(select(User).where(func.lower(User.email) == normalize_email(email)).with_for_update())
    if user is None or not user.is_active or user.email_verified is True:
        return GENERIC_VERIFICATION_MESSAGE
    latest = db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id).order_by(EmailVerificationToken.created_at.desc()).limit(1))
    if latest is not None and utc_aware(latest.created_at) > now - timedelta(seconds=settings.email_verification_cooldown_seconds):
        return GENERIC_VERIFICATION_MESSAGE
    raw = secrets.token_urlsafe(48)
    db.execute(update(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id, EmailVerificationToken.used_at.is_(None)).values(used_at=now))
    record = EmailVerificationToken(
        user_id=user.id, token_hash=hash_credential(raw),
        expires_at=now + timedelta(minutes=settings.email_verification_expire_minutes), created_at=now,
    )
    db.add(record)
    db.flush()
    verification_url = f"{settings.frontend_url.rstrip('/')}/verify-email?{urlencode({'token': raw})}"
    enqueue_secure_email(
        db, recipient=user.email, subject="Verify your PriceYard email",
        body=f"Confirm that you own this email address using this link within {settings.email_verification_expire_minutes} minutes:\n{verification_url}\n\nIf you did not request this, ignore this email. Your 14-day trial still starts at registration.",
        expires_at=record.expires_at, user_id=user.id, event_key=f"email-verification:{record.id}",
        proof_type="email_verification", proof_id=record.id,
    )
    return GENERIC_VERIFICATION_MESSAGE


def verify_email(db: Session, *, token: str) -> str:
    now = datetime.now(timezone.utc)
    token_hash = hash_credential(token)
    owner_id = db.scalar(select(EmailVerificationToken.user_id).where(EmailVerificationToken.token_hash == token_hash))
    if owner_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link is invalid or expired")
    user = db.scalar(select(User).where(User.id == owner_id).with_for_update().execution_options(populate_existing=True))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link is invalid or expired")
    claimed_id = db.scalar(update(EmailVerificationToken).where(
        EmailVerificationToken.token_hash == token_hash,
        EmailVerificationToken.used_at.is_(None), EmailVerificationToken.expires_at > now,
    ).values(used_at=now).returning(EmailVerificationToken.user_id).execution_options(synchronize_session="fetch"))
    if claimed_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link is invalid or expired")
    user.email_verified = True
    db.execute(update(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id, EmailVerificationToken.used_at.is_(None)).values(used_at=now))
    db.flush()
    return "Email verified. Your existing trial and subscription are unchanged."
