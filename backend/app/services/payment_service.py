from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from decimal import Decimal

import requests
from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.payment import Payment
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


def initiate_payment(db: Session, user: User, plan: PaymentPlan) -> PaymentInitiateResponse:
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
        response = requests.post(
            PAYSTACK_INITIALIZE_URL,
            json={
                "email": user.email,
                "amount": int(amount * 100),
                "reference": reference,
                "callback_url": f"{settings.frontend_url}/payment/callback",
            },
            headers={
                "Authorization": f"Bearer {settings.paystack_secret_key}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        body = response.json()
    except (requests.RequestException, ValueError) as exc:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the payment provider",
        ) from exc

    if not response.ok or not body.get("status"):
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not start payment",
        )

    data = body.get("data") or {}
    authorization_url = data.get("authorization_url")
    if not authorization_url:
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
    amount = data.get("amount")
    transaction_id = data.get("id")
    if (type(amount) is not int or amount <= 0 or Decimal(amount) != payment.amount * 100
            or data.get("currency") != "NGN" or payment.currency != "NGN"
            or data.get("status") != "success" or payment.plan not in PLAN_PRICES
            or type(transaction_id) is not int or transaction_id <= 0 or len(str(transaction_id)) > 100):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Payment evidence does not match the recorded purchase")
    if payment.status == "success":
        return

    duplicate = db.scalar(select(Payment.id).where(Payment.paystack_transaction_id == str(transaction_id), Payment.id != payment.id))
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment transaction is already recorded for another purchase")

    try:
        user = db.scalar(select(User).where(User.id == payment.user_id).with_for_update().execution_options(populate_existing=True))
        # Do not use an expiry helper here: its intermediate commit could release
        # the confirmation lock before access and the audit record are saved.
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == payment.user_id).with_for_update().execution_options(populate_existing=True))
        if user is None or subscription is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subscription record is unavailable; payment not applied")
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
