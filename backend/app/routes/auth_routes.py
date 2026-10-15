from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.rate_limit import limiter
from app.services.subscription_service import REFERRAL_REWARD_DAYS
from app.schemas.auth_schema import EmailVerificationRequest, ForgotPasswordRequest, GoogleLinkRequest, GoogleLoginRequest, LoginRequest, MessageResponse, ReferralSummaryResponse, RefreshRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, VerifyEmailRequest
from app.schemas.user_schema import UserResponse
from app.security import decode_access_claims
from app.services.admin_alert_service import notify_admins
from app.services.auth_service import authenticate_or_create_google_user, authenticate_user, link_google_identity, register_user
from app.services.auth_session_service import issue_session, logout_all_sessions, logout_session, refresh_session
from app.services.email_verification_service import request_email_verification, verify_email
from app.services.password_reset_service import request_password_reset, reset_password
from app.utils.permissions import bearer_scheme, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    user = register_user(db, payload)
    request_email_verification(db, email=user.email)
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
    return issue_session(db, user, remember_me=payload.remember_me)


@router.post("/google", response_model=TokenResponse)
@limiter.limit("5/minute")
def login_with_google(request: Request, payload: GoogleLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_or_create_google_user(db, payload.id_token)
    return issue_session(db, user, remember_me=payload.remember_me)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return refresh_session(db, refresh_token=payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> MessageResponse:
    claims = decode_access_claims(credentials.credentials)
    logout_session(db, user_id=current_user.id, session_id=claims["sid"])
    return MessageResponse(message="Signed out of this session.")


@router.post("/logout-all", response_model=MessageResponse)
def logout_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    logout_all_sessions(db, current_user)
    return MessageResponse(message="All sessions have been signed out.")


@router.post("/request-verification", response_model=MessageResponse)
@limiter.limit("5/minute")
def request_verification(request: Request, payload: EmailVerificationRequest, db: Session = Depends(get_db)) -> MessageResponse:
    return MessageResponse(message=request_email_verification(db, email=str(payload.email)))


@router.post("/verify-email", response_model=MessageResponse)
@limiter.limit("10/minute")
def confirm_email(request: Request, payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> MessageResponse:
    return MessageResponse(message=verify_email(db, token=payload.token))


@router.post("/google/link", response_model=UserResponse)
@limiter.limit("5/minute")
def link_google(
    request: Request, payload: GoogleLinkRequest,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> User:
    return link_google_identity(db, current_user, token=payload.id_token, password=payload.password)


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
@limiter.limit("10/minute")
def change_forgotten_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    return MessageResponse(message=reset_password(db, token=payload.token, new_password=payload.new_password))
