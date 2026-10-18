from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security import decode_access_claims
from app.services.login_revocation_service import is_revoked
from app.services.subscription_service import get_subscription_for_user, has_full_access
from app.services.browser_session_service import browser_token, validate_browser_request

class BrowserOrBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        if request.headers.get('authorization') is not None:
            # Explicit invalid bearer credentials must never fall back to a cookie.
            return await super().__call__(request)
        token = browser_token(request)
        if token:
            validate_browser_request(request, token)
            return HTTPAuthorizationCredentials(scheme='Bearer', credentials=token)
        return None


bearer_scheme = BrowserOrBearer(auto_error=False)
VALID_MVP_ROLES = frozenset({"admin", "free_user", "paid_user", "reporter"})


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = decode_access_claims(credentials.credentials)
        user_id = int(claims["sub"])
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if claims.get("auth_version", 0) != user.auth_version or is_revoked(db, credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

    return user


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


def require_full_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if current_user.role == "admin":
        return current_user

    subscription = get_subscription_for_user(db, current_user.id)
    if not has_full_access(subscription):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Full subscription or active trial required",
        )
    return current_user
