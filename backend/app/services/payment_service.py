from __future__ import annotations

import hashlib
import hmac
import secrets
from decimal import Decimal

import requests
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment_schema import PaymentInitiateResponse, PaymentPlan
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.subscription_service import activate_paid_subscription, find_subscription_for_user

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
    if not settings.paystack_secret_key or not signature:
        return False
    expected = hmac.new(settings.paystack_secret_key.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_webhook_event(db: Session, payload: dict) -> None:
    if payload.get("event") != "charge.success":
        return

    data = payload.get("data") or {}
    reference = data.get("reference")
    if not reference:
        return

    payment = db.scalar(select(Payment).where(Payment.reference == reference))
    if payment is None or payment.status == "success":
        return

    payment.status = "success"
    payment.paystack_transaction_id = str(data.get("id") or "") or None
    db.commit()

    subscription = find_subscription_for_user(db, payment.user_id)
    if subscription is None:
        return

    old_value = snapshot_model(subscription)
    activate_paid_subscription(db, subscription, plan=payment.plan)
    create_audit_log(
        db, actor=payment.user, action="payment.success", table_name="subscriptions",
        record_id=subscription.id, old_value=old_value, new_value=snapshot_model(subscription),
    )


def list_payments(db: Session) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.created_at.desc())).all())
