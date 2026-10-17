from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate, UserResponse
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.subscription_service import apply_paid_expiry, apply_trial_expiry
from app.services.user_service import get_user, list_users, prepare_user_update, update_user
from app.utils.permissions import require_roles

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[User]:
    return list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> User:
    return get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> User:
    target, subscription = prepare_user_update(db, user_id)
    old_user = snapshot_model(target)
    old_subscription = snapshot_model(subscription) if subscription is not None else None
    try:
        if subscription is not None:
            apply_trial_expiry(subscription); apply_paid_expiry(subscription)
        target = update_user(db, target, payload, commit=False, prepared=True)
        create_audit_log(
            db, actor=admin, action="user.update", table_name="users",
            record_id=target.id, old_value=old_user, new_value=snapshot_model(target), commit=False,
        )
        if subscription is not None:
            new_subscription = snapshot_model(subscription)
            if old_subscription != new_subscription:
                create_audit_log(
                    db, actor=admin, action="subscription.user_management_sync", table_name="subscriptions",
                    record_id=subscription.id, old_value=old_subscription, new_value=new_subscription, commit=False,
                )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return target
