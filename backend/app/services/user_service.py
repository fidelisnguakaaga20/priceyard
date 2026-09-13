from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate
from app.services.subscription_service import get_subscription_for_user, update_subscription_status


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())


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
    would_deactivate = payload.is_active is False
    would_demote = payload.role is not None and payload.role != "admin"
    if (would_deactivate or would_demote) and _is_last_active_admin(db, user):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate or demote the last active admin account",
        )

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.role == "paid_user":
        subscription = get_subscription_for_user(db, user.id)
        update_subscription_status(db, subscription, "active")
        user.role = "paid_user"
        db.commit()
    elif payload.role == "free_user":
        subscription = get_subscription_for_user(db, user.id)
        update_subscription_status(db, subscription, "free")
        user.role = "free_user"
        db.commit()
    elif payload.role == "admin":
        user.role = "admin"
        db.commit()
    else:
        db.commit()

    db.refresh(user)
    return user
