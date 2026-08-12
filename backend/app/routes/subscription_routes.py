from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription_schema import SubscriptionResponse, SubscriptionStatusUpdate
from app.services.subscription_service import (
    get_subscription_for_user,
    list_subscriptions,
    update_subscription_status,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionResponse])
def get_subscriptions(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[Subscription]:
    return list_subscriptions(db)


@router.get("/{user_id}", response_model=SubscriptionResponse)
def get_user_subscription(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Subscription:
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return get_subscription_for_user(db, user_id)


@router.patch("/{user_id}/status", response_model=SubscriptionResponse)
def set_subscription_status(
    user_id: int,
    payload: SubscriptionStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Subscription:
    subscription = get_subscription_for_user(db, user_id)
    return update_subscription_status(db, subscription, payload.status)
