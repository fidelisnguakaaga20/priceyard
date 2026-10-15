from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.auth_session import AuthSession
from app.security import decode_access_claims
from app.services.auth_session_service import utc_aware
from app.services.subscription_service import find_subscription_for_user, has_full_access

bearer_scheme = HTTPBearer(auto_error=False)
VALID_MVP_ROLES = frozenset({"admin", "free_user", "paid_user", "reporter"})


def _authenticate(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    try:
        if credentials.scheme.lower() != "bearer":
            raise InvalidTokenError("Invalid scheme")
        claims = decode_access_claims(credentials.credentials)
        session_id = claims.get("sid")
        if not isinstance(session_id, str):
            raise InvalidTokenError("Legacy token requires a new sign-in")
        user = db.get(User, int(claims["sub"]))
        session = db.get(AuthSession, session_id)
        now = datetime.now(timezone.utc)
        if user is None or session is None or session.user_id != user.id:
            raise InvalidTokenError("Unknown session")
        if session.revoked_at is not None or utc_aware(session.expires_at) <= now or claims["av"] != user.auth_version:
            raise InvalidTokenError("Revoked session")
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if user.role not in VALID_MVP_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account permissions require review")
    db.info["actor_id"] = user.id
    db.info["actor_role"] = user.role
    return user


def optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    request: Request = None,
) -> User | None:
    if credentials is None and request is not None and request.headers.get("authorization") is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header", headers={"WWW-Authenticate": "Bearer"})
    return None if credentials is None else _authenticate(credentials, db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    return _authenticate(credentials, db)


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)
    unknown = allowed - VALID_MVP_ROLES
    if unknown:
        raise ValueError(f"Unknown role(s): {', '.join(sorted(unknown))}")

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency


def user_has_full_access(db: Session, user: User | None) -> bool:
    if user is None or not user.is_active or user.role not in VALID_MVP_ROLES:
        return False
    if user.role == "admin":
        return True
    subscription = find_subscription_for_user(db, user.id)
    return subscription is not None and has_full_access(subscription)


def require_full_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if not user_has_full_access(db, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Full subscription or active trial required",
        )
    return current_user
