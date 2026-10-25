"""Derived founder protection without changing stored roles or database records."""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate


def normalized_owner_email() -> str:
    return get_settings().owner_email.strip().lower()


def is_protected_owner_account(user: User) -> bool:
    """Protect the configured account even if external recovery changed its role."""
    configured = normalized_owner_email()
    return bool(configured and user.email and user.email.strip().lower() == configured)


def resolve_owner(db: Session) -> User | None:
    """A unique, persisted active Admin must already own the configured email.

    Ambiguous legacy case variants, missing accounts and public/free accounts
    fail closed. This never creates a user or changes a role or subscription.
    """
    configured = normalized_owner_email()
    if not configured:
        return None
    with db.no_autoflush:
        matches = db.scalars(select(User).where(
            func.lower(func.trim(User.email)) == configured
        ).limit(2).execution_options(populate_existing=True)).all()
    if len(matches) != 1:
        return None
    owner = matches[0]
    return owner if owner.id is not None and owner.is_active and owner.role == "admin" else None


def is_owner(db: Session | None, user: User) -> bool:
    # Ordinary records in paged/streamed lists need no additional DB lookup.
    if db is None or user.id is None or not user.is_active or user.role != "admin" or not is_protected_owner_account(user):
        return False
    owner = resolve_owner(db)
    return owner is not None and owner.id == user.id


def authorize_user_update(
    db: Session, target: User, payload: AdminUserUpdate, *,
    actor_id: int, actor_auth_version: int,
) -> User:
    """Recheck the actor after the user-management transaction lock is acquired."""
    with db.no_autoflush:
        actor = db.scalar(select(User).where(User.id == actor_id).execution_options(populate_existing=True))
    if (actor is None or not actor.is_active or actor.role != "admin"
            or actor.auth_version != actor_auth_version):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Your Admin access changed. Sign in again before managing users.")

    actor_is_owner = is_owner(db, actor)
    if is_protected_owner_account(target):
        if not actor_is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only the Owner can manage the protected Owner account")
        if payload.is_active is False or payload.role not in {None, "admin"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="The Owner account cannot be deactivated or demoted")

    if not actor_is_owner and (target.role == "admin" or payload.role == "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only the Owner can appoint or manage Admin accounts")
    return actor
