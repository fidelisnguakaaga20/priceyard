from fastapi import HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate
from app.services.subscription_service import get_subscription_for_user, update_subscription_status
from app.services.auth_session_service import revoke_sessions


def list_users(db: Session, *, page: int = 1, page_size: int = 100) -> list[User]:
    if page < 1 or not 1 <= page_size <= 1000:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    return list(db.scalars(select(User).order_by(User.id).offset((page - 1) * page_size).limit(page_size)).all())


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _is_last_active_admin(db: Session, user: User) -> bool:
    if user.role != "admin" or not user.is_active:
        return False
    other_active_admins = db.scalar(
        select(func.count()).select_from(User).where(
            User.role == "admin", User.is_active.is_(True), User.id != user.id
        )
    )
    return (other_active_admins or 0) == 0


def update_user(db: Session, user: User, payload: AdminUserUpdate) -> User:
    # A transaction-scoped PostgreSQL advisory lock serializes the invariant
    # even when two requests target different administrators.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(724910)"))
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    would_deactivate = payload.is_active is False
    would_demote = payload.role is not None and payload.role != "admin"
    if (would_deactivate or would_demote) and _is_last_active_admin(db, user):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate or demote the last active admin account",
        )

    if payload.is_active is not None:
        if payload.is_active is False and user.is_active:
            revoke_sessions(db, user)
        user.is_active = payload.is_active

    if payload.role == "paid_user":
        subscription = get_subscription_for_user(db, user.id)
        update_subscription_status(db, subscription, "active")
        user.role = "paid_user"
    elif payload.role == "free_user":
        subscription = get_subscription_for_user(db, user.id)
        update_subscription_status(db, subscription, "free")
        user.role = "free_user"
    elif payload.role == "admin":
        user.role = "admin"
    elif payload.role == "reporter":
        user.role = "reporter"
    db.flush()
    return user
