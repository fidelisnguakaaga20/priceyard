from fastapi import HTTPException, status
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.user_schema import AdminUserUpdate
from app.services.owner_policy import authorize_user_update
from app.services.subscription_service import apply_paid_expiry, apply_trial_expiry, lock_subscription_state, update_subscription_status


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


def prepare_user_update(db: Session, user_id: int) -> tuple[User, Subscription | None]:
    if db.get_bind().dialect.name == "postgresql":
        # Serialize privileged role/activity edits across API workers. Keep this
        # transaction open through the final user/subscription change.
        db.execute(text("SELECT pg_advisory_xact_lock(741523, 1)"))
    return lock_subscription_state(db, user_id)


def update_user(
    db: Session, user: User, payload: AdminUserUpdate, *, actor: User,
    actor_auth_version: int | None = None, commit: bool = True, prepared: bool = False,
) -> User:
    actor_id = actor.id
    captured_version = actor.auth_version if actor_auth_version is None else actor_auth_version
    if not prepared:
        user, subscription = prepare_user_update(db, user.id)
    else:
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    authorize_user_update(db, user, payload, actor_id=actor_id, actor_auth_version=captured_version)
    would_deactivate = payload.is_active is False
    would_demote = payload.role is not None and payload.role != "admin"
    if (would_deactivate or would_demote) and _is_last_active_admin(db, user):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate or demote the last active admin account",
        )

    # Policy checks precede every mutation, including subscription expiry cleanup.
    if subscription is not None:
        apply_trial_expiry(subscription)
        apply_paid_expiry(subscription)

    if payload.is_active is not None:
        if user.is_active and payload.is_active is False:
            db.execute(update(User).where(User.id == user.id).values(auth_version=User.auth_version + 1))
        user.is_active = payload.is_active

    if payload.role in {"paid_user", "free_user"}:
        # Avoid expiry helpers that commit independently and release the guard.
        if subscription is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
        update_subscription_status(db, subscription, "active" if payload.role == "paid_user" else "free", commit=False)
        user.role = payload.role
    elif payload.role in {"admin", "reporter"}:
        user.role = payload.role

    db.commit() if commit else db.flush()
    return user
