import secrets
import string

from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.services.subscription_service import build_trial_subscription
from app.schemas.auth_schema import RegisterRequest
from app.utils.password import hash_password, verify_password

REFERRAL_CODE_ALPHABET = "".join(c for c in string.ascii_uppercase + string.digits if c not in "0O1I")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def generate_referral_code(db: Session) -> str:
    for _ in range(20):
        code = "".join(secrets.choice(REFERRAL_CODE_ALPHABET) for _ in range(8))
        if db.scalar(select(User).where(User.referral_code == code)) is None:
            return code
    raise RuntimeError("Could not generate a unique referral code")


def register_user(db: Session, payload: RegisterRequest) -> User:
    email = normalize_email(str(payload.email))

    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    phone = payload.phone.strip() if payload.phone else None
    if phone:
        phone_owner = db.scalar(select(User).where(User.phone == phone))
        if phone_owner is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already registered",
            )

    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    referrer: User | None = None
    if payload.referral_code:
        code = payload.referral_code.strip().upper()
        referrer = db.scalar(select(User).where(User.referral_code == code))
        if referrer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid referral code",
            )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role="free_user",
        is_active=True,
        referral_code=generate_referral_code(db),
        referred_by_id=referrer.id if referrer else None,
        email_verified=False,
    )
    user.subscription = build_trial_subscription(user=user)
    db.add(user)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User account already exists",
        ) from exc

    # A referral is an attribution only; the payment workflow qualifies rewards.
    # The request transaction commits after all related changes are successful.
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    user = db.scalar(select(User).where(func.lower(User.email) == normalized_email).with_for_update().execution_options(populate_existing=True))

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def verify_google_claims(token: str) -> dict:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )

    try:
        claims = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.google_client_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google sign-in token",
        ) from exc

    google_sub = claims.get("sub")
    email = claims.get("email")
    if (
        claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}
        or claims.get("aud") != settings.google_client_id
        or not isinstance(google_sub, str) or not google_sub or len(google_sub) > 255
        or not isinstance(email, str) or not email or len(email) > 320
        or claims.get("email_verified") is not True
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account could not be verified",
        )

    return claims


def authenticate_or_create_google_user(db: Session, token: str) -> User:
    claims = verify_google_claims(token)
    google_sub = claims["sub"]
    normalized_email = normalize_email(claims["email"])
    user = db.scalar(select(User).where(User.google_id == google_sub).with_for_update().execution_options(populate_existing=True))

    if user is None:
        user = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
        if user is not None:
            # Matching email is never sufficient to merge login identities.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account already uses this email. Sign in or reset its password, verify your email, then link Google from your account.",
            )
        else:
            full_name = str(claims.get("name") or normalized_email.split("@")[0]).strip()[:150]
            user = User(
                full_name=full_name or normalized_email,
                email=normalized_email,
                phone=None,
                password_hash=hash_password(secrets.token_urlsafe(32)),
                role="free_user",
                is_active=True,
                google_id=google_sub,
                auth_provider="google",
                email_verified=True,
                referral_code=generate_referral_code(db),
            )
            user.subscription = build_trial_subscription(user=user)
            db.add(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if normalize_email(user.email) == normalized_email:
        # A known provider subject proves this stored email only when it still
        # matches. An unrelated verified email must not change local ownership.
        user.email_verified = True

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account conflict during Google sign-in",
        ) from exc

    return user


def link_google_identity(db: Session, user: User, *, token: str, password: str) -> User:
    claims = verify_google_claims(token)
    locked = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if locked is None or not locked.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    if locked.email_verified is not True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verify your email before linking Google")
    if not verify_password(password, locked.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Confirm your current password to link Google")
    if normalize_email(claims["email"]) != normalize_email(locked.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Google must use your verified account email")
    if locked.google_id is not None and locked.google_id != claims["sub"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A different Google identity is already linked")
    owner = db.scalar(select(User).where(User.google_id == claims["sub"], User.id != locked.id))
    if owner is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Google identity is already linked to another account")
    locked.google_id = claims["sub"]
    locked.auth_provider = "local_google"
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account conflict during Google linking") from exc
    return locked
