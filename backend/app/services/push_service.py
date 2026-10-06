from __future__ import annotations

import json
import logging

from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate

logger = logging.getLogger(__name__)


def save_subscription(db: Session, user: User, payload: PushSubscriptionCreate) -> PushSubscription:
    existing = db.scalar(select(PushSubscription).where(PushSubscription.endpoint == payload.endpoint))
    if existing is not None:
        existing.user_id = user.id
        existing.p256dh = payload.keys.p256dh
        existing.auth = payload.keys.auth
        db.commit()
        db.refresh(existing)
        return existing

    subscription = PushSubscription(
        user_id=user.id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def remove_subscription(db: Session, user: User, endpoint: str) -> None:
    db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == endpoint,
    ).delete()
    db.commit()


def send_push_to_user(db: Session, user_id: int, *, title: str, body: str, url: str) -> int:
    """Best-effort: push to every device this user has subscribed from. A dead/expired
    subscription (404/410) is pruned; any other failure for one device must never block
    sending to the user's other devices or raise into the caller."""
    settings = get_settings()
    if not settings.vapid_public_key or not settings.vapid_private_key:
        return 0

    subscriptions = list(db.scalars(select(PushSubscription).where(PushSubscription.user_id == user_id)).all())
    payload = json.dumps({"title": title, "body": body, "url": url})
    sent = 0
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": f"mailto:{settings.vapid_claim_email}"},
            )
            sent += 1
        except WebPushException as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in (404, 410):
                db.delete(subscription)
                db.commit()
            else:
                logger.warning("Push send failed for subscription %s: %s", subscription.id, exc)
        except Exception as exc:
            logger.warning("Push send failed for subscription %s: %s", subscription.id, exc)
    return sent
