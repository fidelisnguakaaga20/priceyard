from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate, PushUnsubscribeRequest
from app.services.push_service import remove_subscription, save_subscription
from app.utils.permissions import get_current_user

router = APIRouter(prefix="/push", tags=["push"])


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
