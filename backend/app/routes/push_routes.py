from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate, PushUnsubscribeRequest
from app.services.push_service import remove_subscription, save_subscription
from app.utils.permissions import get_current_user

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/subscribed")
def check_subscribed(
    endpoint: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    """A browser only ever holds one push subscription per site -- if a different
    account previously enabled alerts on this same device, that subscription still
    exists and would otherwise look "on" to whoever is logged in now. This confirms
    it actually belongs to the current user before the UI claims alerts are enabled."""
    owned = db.scalar(
        select(PushSubscription).where(
            PushSubscription.endpoint == endpoint,
            PushSubscription.user_id == current_user.id,
        )
    )
    return {"subscribed": owned is not None}


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe(
    payload: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    save_subscription(db, current_user, payload)


@router.post("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(
    payload: PushUnsubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    remove_subscription(db, current_user, payload.endpoint)
