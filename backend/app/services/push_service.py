from __future__ import annotations

import json
import logging
import base64
import binascii
import hmac

from fastapi import HTTPException
from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.schemas.push_schema import PushSubscriptionCreate
from app.utils.push_validation import SafePushSession

logger = logging.getLogger(__name__)


def _same_device_key(stored: str, supplied: str) -> bool:
    try:
        old = base64.b64decode(stored+"="*(-len(stored)%4), altchars=b"-_", validate=True)
        new = base64.b64decode(supplied+"="*(-len(supplied)%4), altchars=b"-_", validate=True)
        return hmac.compare_digest(old, new)
    except (ValueError, binascii.Error):
        return False


def save_subscription(db: Session, user: User, payload: PushSubscriptionCreate) -> PushSubscription:
    statement = select(PushSubscription).where(PushSubscription.endpoint == payload.endpoint).with_for_update().execution_options(populate_existing=True)
    existing = db.scalar(statement)
    if existing is None:
        subscription = PushSubscription(user_id=user.id, endpoint=payload.endpoint,
                                        p256dh=payload.keys.p256dh, auth=payload.keys.auth)
        try:
            with db.begin_nested():
                db.add(subscription)
                db.flush()
        except IntegrityError:
            # Another worker may have registered this endpoint first. Recover
            # only that conflict, then apply the same ownership proof below.
            existing = db.scalar(statement)
            if existing is None:
                raise
        else:
            db.commit()
            db.refresh(subscription)
            return subscription
    if existing is not None:
        if existing.user_id != user.id:
            same_public = _same_device_key(existing.p256dh, payload.keys.p256dh)
            same_secret = _same_device_key(existing.auth, payload.keys.auth)
            if not (same_public and same_secret):
                raise HTTPException(status_code=409, detail="Push subscription belongs to another account")
        existing.user_id = user.id
        existing.p256dh = payload.keys.p256dh
        existing.auth = payload.keys.auth
        db.commit()
        db.refresh(existing)
        return existing

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
            info = PushSubscriptionCreate.model_validate({
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            })
            with SafePushSession() as transport:
                webpush(
                    subscription_info=info.model_dump(),
                    data=payload,
                    vapid_private_key=settings.vapid_private_key,
                    vapid_claims={"sub": f"mailto:{settings.vapid_claim_email}"},
                    timeout=7,
                    requests_session=transport,
                )
            sent += 1
        except WebPushException as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in (404, 410):
                db.delete(subscription)
                db.commit()
            else:
                logger.warning("Push send failed for subscription %s", subscription.id)
        except Exception:
            logger.warning("Push send failed for subscription %s", subscription.id)
    return sent
