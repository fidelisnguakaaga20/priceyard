from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.rate_limit import limiter
from app.services.subscription_service import REFERRAL_REWARD_DAYS
from app.schemas.auth_schema import ForgotPasswordRequest, GoogleLoginRequest, LoginRequest, MessageResponse, ReferralSummaryResponse, RegisterRequest, ResetPasswordRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.security import create_access_token
from app.services.admin_alert_service import notify_admins
from app.services.auth_service import authenticate_or_create_google_user, authenticate_user, register_user
from app.services.password_reset_service import request_password_reset, reset_password
from app.utils.permissions import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    user = register_user(db, payload)
    notify_admins(
        db,
        subject="New PriceYard signup",
        body=f"A new user just registered on PriceYard:\n\nName: {user.full_name}\nEmail: {user.email}\nPhone: {user.phone or '-'}",
    )
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, email=str(payload.email), password=payload.password)
    return TokenResponse(access_token=create_access_token(user_id=user.id))


@router.post("/google", response_model=TokenResponse)
@limiter.limit("5/minute")
def login_with_google(request: Request, payload: GoogleLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_or_create_google_user(db, payload.id_token)
    return TokenResponse(access_token=create_access_token(user_id=user.id))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/referral-summary", response_model=ReferralSummaryResponse)
def referral_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReferralSummaryResponse:
    referred_count = db.scalar(
        select(func.count()).select_from(User).where(User.referred_by_id == current_user.id)
    )
    return ReferralSummaryResponse(
        referral_code=current_user.referral_code,
        referred_count=referred_count or 0,
        reward_days=REFERRAL_REWARD_DAYS,
    )


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    return MessageResponse(message=request_password_reset(db, email=str(payload.email)))


@router.post("/reset-password", response_model=MessageResponse)
def change_forgotten_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    return MessageResponse(message=reset_password(db, token=payload.token, new_password=payload.new_password))
