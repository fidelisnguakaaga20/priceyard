from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate, UserResponse
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.subscription_service import get_subscription_for_user
from app.services.user_service import get_user, list_users, update_user
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
    target = get_user(db, user_id)
    old_user = snapshot_model(target)
    subscription = get_subscription_for_user(db, user_id)
    old_subscription = snapshot_model(subscription)
    target = update_user(db, target, payload)
    create_audit_log(
        db, actor=admin, action="user.update", table_name="users",
        record_id=target.id, old_value=old_user, new_value=snapshot_model(target),
    )
    new_subscription = snapshot_model(subscription)
    if old_subscription != new_subscription:
        create_audit_log(
            db, actor=admin, action="subscription.user_management_sync", table_name="subscriptions",
            record_id=subscription.id, old_value=old_subscription, new_value=new_subscription,
        )
    return target
