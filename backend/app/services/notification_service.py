"""Durable, independently retried delivery; never contacts providers on approval."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import uuid
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.notification_job import NotificationJob


def _mail_cipher() -> Fernet:
    from app.security import _jwt_secret
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"priceyard-notification-v1",
               info=b"temporary-account-proof-emails").derive(_jwt_secret().encode("utf-8"))
    return Fernet(base64.urlsafe_b64encode(key))


def enqueue_secure_email(db: Session, *, recipient: str, subject: str, body: str,
                         expires_at: datetime, user_id: int, event_key: str,
                         proof_type: str | None = None, proof_id: int | None = None) -> bool:
    """Raw account-proof links exist only in authenticated ciphertext at rest."""
    ciphertext = _mail_cipher().encrypt(json.dumps({"subject": subject, "body": body}).encode("utf-8")).decode("ascii")
    return enqueue_notification(db, channel="email", recipient=recipient, event_key=event_key,
                                payload={"encrypted_message": ciphertext, "_expires_at": expires_at.isoformat(), "_user_id": user_id,
                                         "_proof_type": proof_type, "_proof_id": proof_id})


def delivery_payload(payload: dict) -> dict:
    if "encrypted_message" in payload:
        return json.loads(_mail_cipher().decrypt(payload["encrypted_message"].encode("ascii")))
    return {key: value for key, value in payload.items() if not key.startswith("_")}


def _eligible_payload(db: Session, payload: dict, now: datetime) -> bool:
    from app.models.user import User
    from app.utils.permissions import user_has_full_access
    if payload.get("_expires_at"):
        expiry = datetime.fromisoformat(payload["_expires_at"])
        if expiry.tzinfo is None or expiry <= now:
            return False
    if payload.get("_user_id"):
        user = db.scalar(select(User).where(User.id == payload["_user_id"]).execution_options(populate_existing=True))
        if user is None or not user.is_active:
            return False
        if payload.get("_requires_full_access") and not user_has_full_access(db, user):
            return False
    if payload.get("_proof_id"):
        from app.models.password_reset_token import PasswordResetToken
        from app.models.email_verification_token import EmailVerificationToken
        proof_model = {"password_reset": PasswordResetToken, "email_verification": EmailVerificationToken}.get(payload.get("_proof_type"))
        if proof_model is None:
            return False
        proof = db.scalar(select(proof_model).where(
            proof_model.id == payload["_proof_id"], proof_model.user_id == payload.get("_user_id"),
            proof_model.used_at.is_(None), proof_model.expires_at > now,
        ))
        if proof is None:
            return False
    if payload.get("_trial_subscription_id"):
        from app.models.subscription import Subscription
        from app.services.subscription_service import aware_utc, paid_cutoff
        subscription = db.scalar(select(Subscription).where(
            Subscription.id == payload["_trial_subscription_id"], Subscription.user_id == payload.get("_user_id"),
        ).execution_options(populate_existing=True))
        if subscription is None or subscription.status != "trial" or subscription.trial_ends_at is None:
            return False
        if aware_utc(subscription.trial_ends_at).isoformat() != payload.get("_trial_ends_at"):
            return False
        purchased_until = paid_cutoff(subscription)
        if subscription.manual_grant or (purchased_until is not None and purchased_until > now):
            return False
    if payload.get("_price_update_id"):
        from app.models.price_update import PriceUpdate
        from app.services.watchlist_alert_service import current_public_observation, watch_matches, _target_condition_met
        from app.models.watchlist import Watchlist
        from app.services.auth_session_service import utc_aware
        price = db.scalar(select(PriceUpdate).where(PriceUpdate.id == payload["_price_update_id"]).execution_options(populate_existing=True))
        if price is None or not current_public_observation(db, price):
            return False
        if payload.get("_price_revision") and utc_aware(price.updated_at).isoformat() != payload["_price_revision"]:
            return False
        if payload.get("_watchlist_ids"):
            watches = db.scalars(select(Watchlist).where(Watchlist.id.in_(payload["_watchlist_ids"]), Watchlist.user_id == payload.get("_user_id")).execution_options(populate_existing=True)).all()
            if not any(watch_matches(item, price) and _target_condition_met(item, price) for item in watches):
                return False
    return True


def enqueue_notification(db: Session, *, channel: str, recipient: str, payload: dict, event_key: str) -> bool:
    if channel not in {"email", "push", "whatsapp"}:
        raise ValueError("Unsupported notification channel")
    if not recipient or len(recipient) > 320 or not event_key or len(json.dumps(payload)) > 24_000:
        raise ValueError("Notification exceeds supported limits")
    key = sha256((event_key + ":" + channel + ":" + recipient).encode()).hexdigest()
    if db.scalar(select(NotificationJob.id).where(NotificationJob.deduplication_key == key)):
        return False
    try:
        with db.begin_nested():
            db.add(NotificationJob(deduplication_key=key, channel=channel, recipient=recipient,
                                   payload=payload, available_at=datetime.now(timezone.utc)))
            db.flush()
    except IntegrityError:
        return False
    return True


def process_notifications(db: Session, *, limit: int = 50, senders: dict | None = None) -> dict:
    """Worker-owned transactions. A lease permits recovery after worker failure.

    At-least-once transport cannot promise exactly-once provider delivery after a
    crash between sending and acknowledgement; logical enqueue is deduplicated.
    """
    from app.services.email_service import send_email
    from app.services.push_service import send_push_to_user
    from app.services.whatsapp_service import send_whatsapp_message
    from app.database import AtomicSession
    if isinstance(db, AtomicSession):
        raise RuntimeError("Notification delivery requires a dedicated worker transaction")
    defaults = {
        "email": lambda job: send_email(recipient=job.recipient, **delivery_payload(job.payload)),
        "push": lambda job: bool(send_push_to_user(db, int(job.recipient), **delivery_payload(job.payload))),
        "whatsapp": lambda job: send_whatsapp_message(to_phone=job.recipient, **delivery_payload(job.payload)),
    }
    defaults.update(senders or {})
    counts = {"sent": 0, "retried": 0, "failed": 0, "skipped": 0}
    for _ in range(min(max(limit, 1), 100)):
        now = datetime.now(timezone.utc)
        job = db.scalar(select(NotificationJob).where(
            NotificationJob.status.in_(["pending", "processing"]), NotificationJob.available_at <= now
        ).order_by(NotificationJob.id).with_for_update(skip_locked=True).limit(1))
        if job is None:
            break
        lease = str(uuid.uuid4())
        job.status = "processing"; job.attempts += 1; job.available_at = now + timedelta(minutes=5)
        job.lease_token = lease
        db.commit()
        result = "sent"
        error_code = None
        completed_at = None
        available_at = job.available_at
        try:
            if not _eligible_payload(db, job.payload, datetime.now(timezone.utc)):
                result = "skipped"
            else:
                delivered = defaults[job.channel](job)
                if delivered is False:
                    result = "skipped"
            completed_at = datetime.now(timezone.utc)
        except Exception as error:
            # Store only the exception class, never provider payloads/credentials.
            error_code = type(error).__name__[:80]
            if job.attempts >= get_settings().notification_max_attempts:
                result = "failed"
            else:
                result = "pending"
                available_at = now + timedelta(seconds=min(3600, 30 * 2 ** job.attempts))
        # A stale worker must not acknowledge a lease claimed by another worker.
        finalized = db.execute(update(NotificationJob).where(NotificationJob.id == job.id, NotificationJob.lease_token == lease)
                               .values(status=result, available_at=available_at, completed_at=completed_at,
                                       error_code=error_code, lease_token=None).execution_options(synchronize_session="fetch"))
        db.commit()
        if finalized.rowcount:
            counts["retried" if result == "pending" else result] += 1
    return counts
