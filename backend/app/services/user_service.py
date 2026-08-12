from fastapi import HTTPException, status
from sqlalchemy import select
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


def update_user(db: Session, user: User, payload: AdminUserUpdate) -> User:
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
