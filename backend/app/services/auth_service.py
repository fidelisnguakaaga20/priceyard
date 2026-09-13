import secrets

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


def normalize_email(email: str) -> str:
    return email.strip().lower()


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

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role="free_user",
        is_active=True,
    )
    user.subscription = build_trial_subscription(user=user)
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User account already exists",
        ) from exc

    # SessionLocal uses expire_on_commit=False and PostgreSQL/SQLAlchemy returns
    # generated fields during INSERT, so avoid a second database round trip after
    # a successful commit. This prevents a transient pooler disconnect after the
    # commit from turning a successfully created account into a false HTTP 500.
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    user = db.scalar(select(User).where(func.lower(User.email) == normalized_email))

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


def authenticate_or_create_google_user(db: Session, token: str) -> User:
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
    if not google_sub or not email or not claims.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account could not be verified",
        )

    normalized_email = normalize_email(email)
    user = db.scalar(select(User).where(User.google_id == google_sub))

    if user is None:
        user = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
        if user is not None:
            user.google_id = google_sub
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
            )
            user.subscription = build_trial_subscription(user=user)
            db.add(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account conflict during Google sign-in",
        ) from exc

    db.refresh(user)
    return user
