from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.rate_limit import limiter
from app.services.subscription_service import REFERRAL_REWARD_DAYS
from app.schemas.auth_schema import ForgotPasswordRequest, GoogleLoginRequest, LoginRequest, MessageResponse, ReferralSummaryResponse, RegisterRequest, ResetPasswordRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.security import create_access_token, decode_access_claims
from app.services.login_revocation_service import revoke_token
from app.services.admin_alert_service import notify_admins
from app.services.auth_service import authenticate_or_create_google_user, authenticate_user, register_user
from app.services.password_reset_service import request_password_reset, reset_password
from app.utils.permissions import bearer_scheme, get_current_user
from app.schemas.auth_schema import BrowserLoginRequest, BrowserGoogleLoginRequest, BrowserUpgradeRequest, BrowserSessionResponse
from app.services.browser_session_service import browser_token, clear_browser_session, require_browser_origin, session_metadata, set_browser_session

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
@limiter.shared_limit("5/minute", scope="password-login")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, email=str(payload.email), password=payload.password)
    return TokenResponse(access_token=create_access_token(user_id=user.id, auth_version=user.auth_version))


@router.post("/google", response_model=TokenResponse)
@limiter.shared_limit("5/minute", scope="google-login")
def login_with_google(request: Request, payload: GoogleLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_or_create_google_user(db, payload.id_token)
    return TokenResponse(access_token=create_access_token(user_id=user.id, auth_version=user.auth_version))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> Response:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        claims = decode_access_claims(credentials.credentials)
    except InvalidTokenError:
        response = Response(status_code=204)
        if not request.headers.get('authorization'): clear_browser_session(response, request)
        return response
    user = db.get(User, int(claims["sub"]))
    if user is not None and claims.get("auth_version", 0) == user.auth_version:
        revoke_token(db, user, credentials.credentials, expires_at=datetime.fromtimestamp(claims["exp"], timezone.utc))
    response = Response(status_code=204)
    if not request.headers.get('authorization'): clear_browser_session(response, request)
    return response


def _replace_browser_session(db: Session, request: Request) -> None:
    previous = browser_token(request)
    if not previous: return
    try: claims = decode_access_claims(previous)
    except InvalidTokenError: return
    user = db.get(User, int(claims['sub']))
    if user is not None and claims.get('auth_version', 0) == user.auth_version:
        revoke_token(db, user, previous, expires_at=datetime.fromtimestamp(claims['exp'], timezone.utc))


@router.post('/browser/login', response_model=BrowserSessionResponse)
@limiter.shared_limit('5/minute', scope='password-login')
def browser_login(request: Request, response: Response, payload: BrowserLoginRequest, db: Session = Depends(get_db)):
    require_browser_origin(request)
    user = authenticate_user(db, email=str(payload.email), password=payload.password)
    _replace_browser_session(db, request)
    return set_browser_session(response, request, create_access_token(user_id=user.id, auth_version=user.auth_version), remember=payload.remember)


@router.post('/browser/google', response_model=BrowserSessionResponse)
@limiter.shared_limit('5/minute', scope='google-login')
def browser_google(request: Request, response: Response, payload: BrowserGoogleLoginRequest, db: Session = Depends(get_db)):
    require_browser_origin(request)
    user = authenticate_or_create_google_user(db, payload.id_token)
    _replace_browser_session(db, request)
    return set_browser_session(response, request, create_access_token(user_id=user.id, auth_version=user.auth_version), remember=payload.remember)


@router.get('/browser/session', response_model=BrowserSessionResponse)
def browser_session(request: Request, response: Response, db: Session = Depends(get_db)):
    token = browser_token(request)
    if not token: raise HTTPException(status_code=401, detail='Not authenticated')
    get_current_user(HTTPAuthorizationCredentials(scheme='Bearer', credentials=token), db)
    response.headers['Cache-Control'] = 'private, no-store'
    return session_metadata(token)


@router.post('/browser/upgrade', response_model=BrowserSessionResponse)
def browser_upgrade(request: Request, response: Response, payload: BrowserUpgradeRequest,
                    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)):
    require_browser_origin(request)
    if not request.headers.get('authorization') or credentials is None:
        raise HTTPException(status_code=401, detail='Existing bearer credential required')
    get_current_user(credentials, db)
    if browser_token(request) and browser_token(request) != credentials.credentials:
        raise HTTPException(status_code=409, detail='A browser session already exists')
    # Transport conversion cannot extend the original login lifetime.
    return set_browser_session(response, request, credentials.credentials, remember=payload.remember)


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
