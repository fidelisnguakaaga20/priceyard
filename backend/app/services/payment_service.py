from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from decimal import Decimal
from urllib.parse import quote, urlsplit

import requests
from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.payment_schema import PaymentInitiateResponse, PaymentPlan
from app.services.admin_alert_service import notify_admins
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.subscription_service import activate_paid_subscription

logger = logging.getLogger(__name__)

PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"

# Configurable here - update these if pricing changes. Storage business is
# seasonal, so a discounted multi-month bundle is offered alongside monthly.
PLAN_PRICES: dict[str, Decimal] = {
    "monthly": Decimal("2500.00"),
    "seasonal": Decimal("6000.00"),
}


def _valid_checkout_url(value: object) -> bool:
    if (not isinstance(value, str) or not 1 <= len(value) <= 2048
            or any(ord(char) <= 32 or ord(char) >= 127 for char in value)
            or "\\" in value or "#" in value):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and parsed.hostname == "checkout.paystack.com"
                and parsed.username is None and parsed.password is None
                and parsed.port in {None, 443} and parsed.path not in {"", "/"})
    except ValueError:
        return False


def initiate_payment(db: Session, user: User, plan: PaymentPlan) -> PaymentInitiateResponse:
    subscription = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if subscription is not None and subscription.status == "active" and subscription.end_date is None:
        raise HTTPException(status_code=409, detail="Your account already has indefinite access. Contact support before buying a plan.")
    settings = get_settings()
    if not settings.paystack_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are not configured yet",
        )

    amount = PLAN_PRICES[plan]
    reference = f"py_{secrets.token_hex(12)}"

    payment = Payment(user_id=user.id, reference=reference, plan=plan, amount=amount, currency="NGN", status="pending")
    db.add(payment)
    db.commit()

    try:
        with requests.Session() as transport:
            transport.trust_env = False
            response = transport.post(
                PAYSTACK_INITIALIZE_URL,
                json={
                    "email": user.email,
                    "amount": int(amount * 100),
                    "currency": "NGN",
                    "reference": reference,
                    "callback_url": f"{settings.frontend_url}/payment/callback",
                },
                headers={
                    "Authorization": f"Bearer {settings.paystack_secret_key}",
                    "Content-Type": "application/json",
                },
                timeout=(3, 15), allow_redirects=False, verify=True,
            )
        body = response.json()
    except (requests.RequestException, ValueError):
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the payment provider",
        ) from None

    if not 200 <= response.status_code < 300 or not isinstance(body, dict) or body.get("status") is not True:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not start payment",
        )

    data = body.get("data")
    authorization_url = data.get("authorization_url") if isinstance(data, dict) else None
    if not _valid_checkout_url(authorization_url) or data.get("reference") != reference:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider did not return a checkout link",
        )

    return PaymentInitiateResponse(authorization_url=authorization_url, reference=reference)


def verify_webhook_signature(raw_body: bytes, signature: str | None) -> bool:
    settings = get_settings()
    if (not settings.paystack_secret_key or not isinstance(signature, str)
            or len(signature) != 128 or any(char not in "0123456789abcdefABCDEF" for char in signature)):
        return False
    expected = hmac.new(settings.paystack_secret_key.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature.lower())


def _validate_recorded_evidence(payment: Payment, data: dict, *, allow_unconfirmed: bool = False) -> None:
    amount, transaction_id = data.get("amount"), data.get("id")
    allowed = {"success", "abandoned", "failed", "ongoing", "pending", "processing", "queued", "reversed"} if allow_unconfirmed else {"success"}
    if (data.get("reference") != payment.reference
            or type(amount) is not int or amount <= 0 or Decimal(amount) != payment.amount * 100
            or data.get("currency") != "NGN" or payment.currency != "NGN"
            or not isinstance(data.get("status"), str) or data["status"] not in allowed or payment.plan not in PLAN_PRICES
            or type(transaction_id) is not int or transaction_id <= 0 or len(str(transaction_id)) > 100):
        raise HTTPException(status_code=422, detail="Payment evidence does not match the recorded purchase")


def verify_recorded_payment(db: Session, user: User, reference: str) -> Payment:
    payment = db.scalar(select(Payment).where(Payment.reference == reference, Payment.user_id == user.id))
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status == "success":
        return payment
    settings = get_settings()
    if not settings.paystack_secret_key:
        raise HTTPException(status_code=503, detail="Payments are not configured yet")
    try:
        with requests.Session() as transport:
            transport.trust_env = False
            response = transport.get(
                "https://api.paystack.co/transaction/verify/"+quote(reference, safe=""),
                headers={"Authorization": f"Bearer {settings.paystack_secret_key}"},
                timeout=(3, 15), allow_redirects=False, verify=True,
            )
        body = response.json()
    except (requests.RequestException, ValueError):
        raise HTTPException(status_code=502, detail="Could not reach the payment provider") from None
    if (not 200 <= response.status_code < 300 or not isinstance(body, dict)
            or body.get("status") is not True or not isinstance(body.get("data"), dict)):
        raise HTTPException(status_code=502, detail="Could not verify payment")
    data = body["data"]
    _validate_recorded_evidence(payment, data, allow_unconfirmed=True)
    if data["status"] == "success":
        # Share the webhook's locks/transaction/audit/replay protection. Callback
        # query parameters themselves are never evidence that money was received.
        handle_webhook_event(db, {"event": "charge.success", "data": data})
    db.refresh(payment)
    return payment


def handle_webhook_event(db: Session, payload: dict) -> None:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")
    if payload.get("event") != "charge.success":
        return

    data = payload.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payment evidence")
    reference = data.get("reference")
    if not isinstance(reference, str) or not reference or len(reference) > 100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payment evidence")

    # Serialize confirmation across processes, including duplicate provider IDs
    # on different purchases. Hold through payment, access and audit commit.
    # SQLite is used only for unit/preview tests; PostgreSQL races are tested too.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(741523, 2)"))
    payment = db.scalar(select(Payment).where(Payment.reference == reference).with_for_update().execution_options(populate_existing=True))
    if payment is None:
        return

    # Compare integer kobo against the amount frozen in the original payment,
    # never browser-supplied prices or a possibly changed current price list.
    transaction_id = data.get("id")
    _validate_recorded_evidence(payment, data)
    if payment.paystack_transaction_id is not None and payment.paystack_transaction_id != str(transaction_id):
        raise HTTPException(status_code=409, detail="Payment transaction conflicts with previously recorded evidence")
    if payment.status == "success":
        return

    duplicate = db.scalar(select(Payment.id).where(Payment.paystack_transaction_id == str(transaction_id), Payment.id != payment.id))
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment transaction is already recorded for another purchase")

    held_for_review = False
    try:
        user = db.scalar(select(User).where(User.id == payment.user_id).with_for_update().execution_options(populate_existing=True))
        # Do not use an expiry helper here: its intermediate commit could release
        # the confirmation lock before access and the audit record are saved.
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == payment.user_id).with_for_update().execution_options(populate_existing=True))
        if user is None or subscription is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subscription record is unavailable; payment not applied")
        if subscription.status == "active" and subscription.end_date is None:
            old_value = snapshot_model(payment)
            payment.status = "pending"  # Confirmed funds, activation held; no days consumed.
            payment.paystack_transaction_id = str(transaction_id)
            already_logged = db.scalar(select(AuditLog.id).where(
                AuditLog.action == "payment.review_required", AuditLog.table_name == "payments",
                AuditLog.record_id == payment.id,
            ).limit(1))
            if already_logged is None:
                create_audit_log(db, actor=user, action="payment.review_required", table_name="payments",
                                 record_id=payment.id, old_value=old_value, new_value=snapshot_model(payment), commit=False)
            held_for_review = True
        else:
            old_value = snapshot_model(subscription)
            payment.status = "success"
            payment.paystack_transaction_id = str(transaction_id)
            activate_paid_subscription(db, subscription, plan=payment.plan, commit=False)
            subscription.payment_reference = payment.reference
            create_audit_log(
                db, actor=user, action="payment.success", table_name="subscriptions",
                record_id=subscription.id, old_value=old_value, new_value=snapshot_model(subscription), commit=False,
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    if held_for_review:
        raise HTTPException(status_code=409, detail="Payment confirmed; activation requires manual review while indefinite access remains active")

    try:
        notify_admins(
            db,
            subject="New PriceYard payment received",
            body=(
                f"A payment was just confirmed on PriceYard:\n\n"
                f"User: {payment.user.full_name} ({payment.user.email})\n"
                f"Plan: {payment.plan}\nAmount: NGN {payment.amount:,.2f}\nReference: {payment.reference}"
            ),
        )
    except Exception:
        db.rollback()
        # Never log provider bodies, payment details or credentials on failures.
        logger.error("Payment confirmation saved; administrator notification failed")


def list_payments(db: Session) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.created_at.desc())).all())
