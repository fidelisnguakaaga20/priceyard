from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlparse

import requests
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.payment import Payment
from app.models.entitlement_grant import EntitlementGrant
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.payment_schema import PaymentInitiateResponse, PaymentPlan
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.subscription_service import (
    PAID_PLAN_DURATIONS_DAYS, activate_paid_subscription, is_manual_grant,
    paid_cutoff, qualify_referral_reward, utc_now,
)

PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"

# Configurable here - update these if pricing changes. Storage business is
# seasonal, so a discounted multi-month bundle is offered alongside monthly.
PLAN_PRICES: dict[str, Decimal] = {
    "monthly": Decimal("2500.00"),
    "seasonal": Decimal("6000.00"),
}


def initiate_payment(db: Session, user: User, plan: PaymentPlan) -> PaymentInitiateResponse:
    if user.role == "admin":
        raise HTTPException(status_code=409, detail="Administrator access does not require a subscription purchase")
    settings = get_settings()
    if not settings.paystack_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are not configured yet",
        )

    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=422, detail="Invalid payment plan")
    subscription = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if subscription is not None and is_manual_grant(subscription):
        raise HTTPException(status_code=409, detail="Your account already has a manual access grant; contact support before purchasing")
    environment = provider_environment(settings.paystack_secret_key)
    if environment is None:
        raise HTTPException(status_code=503, detail="Payment provider configuration is invalid")
    amount = PLAN_PRICES[plan]
    reference = f"py_{secrets.token_hex(12)}"

    payment = Payment(
        user_id=user.id, reference=reference, plan=plan, amount=amount,
        currency="NGN", status="pending", duration_days=PAID_PLAN_DURATIONS_DAYS[plan],
        expected_customer_email=user.email.lower().strip(), provider_environment=environment,
    )
    db.add(payment)
    db.flush()
    # Persist the purchase intent before asking an external provider to create
    # checkout. A later HTTP failure must not erase the reference needed to
    # reconcile an eventual signed provider event. This deliberate transaction
    # boundary contains only the newly created pending intent, no access grant.
    Session.commit(db)

    try:
        response = requests.post(
            PAYSTACK_INITIALIZE_URL,
            json={
                "email": user.email,
                "amount": int(amount * 100),
                "reference": reference,
                "currency": "NGN",
                "metadata": {"priceyard_user_id": user.id, "priceyard_reference": reference},
                "callback_url": f"{settings.frontend_url}/payment/callback",
            },
            headers={
                "Authorization": f"Bearer {settings.paystack_secret_key}",
                "Content-Type": "application/json",
            },
            timeout=15,
            allow_redirects=False,
        )
        body = response.json()
    except (requests.RequestException, ValueError) as exc:
        payment.status = "failed"
        db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the payment provider",
        ) from exc

    if not response.ok or not isinstance(body, dict) or body.get("status") is not True:
        payment.status = "failed"
        db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not start payment",
        )

    data = body.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Payment provider returned an invalid checkout response")
    authorization_url = data.get("authorization_url")
    parsed_checkout = urlparse(authorization_url) if isinstance(authorization_url, str) else None
    try:
        checkout_valid = (parsed_checkout is not None and parsed_checkout.scheme == "https"
                          and parsed_checkout.hostname == "checkout.paystack.com"
                          and not parsed_checkout.username and not parsed_checkout.password
                          and parsed_checkout.port in (None, 443) and not parsed_checkout.fragment
                          and data.get("reference") == reference)
    except ValueError:
        checkout_valid = False
    if not checkout_valid:
        payment.status = "failed"
        db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider did not return a checkout link",
        )

    return PaymentInitiateResponse(authorization_url=authorization_url, reference=reference)


def verify_webhook_signature(raw_body: bytes, signature: str | None) -> bool:
    settings = get_settings()
    if not settings.paystack_secret_key or not signature or len(signature) != 128 or any(c not in "0123456789abcdefABCDEF" for c in signature):
        return False
    expected = hmac.new(settings.paystack_secret_key.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature.lower())


def provider_environment(secret_key: str) -> str | None:
    if secret_key.startswith("sk_test_"):
        return "test"
    if secret_key.startswith("sk_live_"):
        return "live"
    return None


def handle_webhook_event(
    db: Session, payload: dict, *, actor: User | None = None,
    legacy_resolution: str | None = None, reason: str | None = None,
) -> str:
    """Apply validated provider evidence in the caller's transaction.

    HTTP entry points verify the signature over the original bytes first.
    User locks serialize purchases and referral rewards; the request boundary
    commits payment, grant, subscription and audits together or rolls all back.
    """
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payment event")
    if payload.get("event") != "charge.success":
        return "ignored_event"

    data = payload.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid payment event data")
    reference = data.get("reference")
    if not isinstance(reference, str) or not 1 <= len(reference) <= 100:
        raise HTTPException(status_code=400, detail="Invalid payment reference")

    payment = db.scalar(select(Payment).where(Payment.reference == reference))
    if payment is None:
        return "unknown_reference"

    # Lock shared user rows in stable order, including the possible referrer.
    # This also serializes different payments for a user and campaign-cap checks.
    lock_ids = {payment.user_id}
    if payment.user.referred_by_id is not None:
        lock_ids.add(payment.user.referred_by_id)
    list(db.scalars(select(User).where(User.id.in_(sorted(lock_ids))).order_by(User.id).with_for_update()).all())
    payment = db.scalar(select(Payment).where(Payment.id == payment.id).with_for_update().execution_options(populate_existing=True))
    if payment.access_applied:
        return "already_applied"

    mismatch = validate_payment_evidence(payment, data)
    if mismatch is not None:
        payment.reconciliation_error = mismatch
        db.flush()
        return "evidence_mismatch"

    transaction_id = str(data["id"])
    was_legacy = payment.requires_reconciliation
    if was_legacy:
        if actor is None or actor.role != "admin" or legacy_resolution not in ("already_applied", "apply_missing") or not reason:
            return "review_required"
        if legacy_resolution == "already_applied":
            # Record reviewed acknowledgement, not a guessed historical grant.
            payment.requires_reconciliation = False
            payment.reconciliation_resolution = "already_applied"
            payment.reconciliation_error = None
            create_audit_log(
                db, actor=actor, action="payment.legacy_reconciled", table_name="payments",
                record_id=payment.id, new_value={"resolution": legacy_resolution, "reason": reason},
            )
            db.flush()
            return "already_applied"

    duplicate = db.scalar(select(Payment.id).where(
        Payment.paystack_transaction_id == transaction_id, Payment.id != payment.id,
    ).limit(1))
    if duplicate is not None:
        payment.reconciliation_error = "provider_transaction_reused"
        db.flush()
        return "evidence_mismatch"

    payment.status = "success"
    payment.paystack_transaction_id = transaction_id
    payment.confirmed_at = payment.confirmed_at or utc_now()

    subscription = db.scalar(select(Subscription).where(Subscription.user_id == payment.user_id).with_for_update().execution_options(populate_existing=True))
    if subscription is None:
        subscription = Subscription(user_id=payment.user_id, status="free", plan_name="free")
        db.add(subscription)
        db.flush()

    old_value = snapshot_model(subscription)
    now = utc_now()
    manual = is_manual_grant(subscription)
    activate_paid_subscription(db, subscription, plan=payment.plan, duration_days=payment.duration_days, now=now)
    expiry = now + timedelta(days=payment.duration_days) if manual else paid_cutoff(subscription)
    db.add(EntitlementGrant(
        payment_id=payment.id, user_id=payment.user_id, duration_days=payment.duration_days,
        starts_at=expiry - timedelta(days=payment.duration_days), expires_at=expiry,
        disposition="manual_grant_preserved" if manual else "applied",
    ))
    payment.entitlement_applied_at = now
    payment.granted_expires_at = None if manual else expiry
    payment.requires_reconciliation = False
    payment.reconciliation_resolution = legacy_resolution
    payment.reconciliation_error = None
    subscription.payment_reference = payment.reference
    db.flush()
    create_audit_log(
        db, actor=actor or payment.user, action="payment.success", table_name="subscriptions",
        record_id=subscription.id, old_value=old_value, new_value=snapshot_model(subscription),
    )
    if reason:
        create_audit_log(db, actor=actor or payment.user, action="payment.reconciliation", table_name="payments", record_id=payment.id, new_value={"resolution": legacy_resolution, "reason": reason})
    if not was_legacy and qualify_referral_reward(db, payment):
        create_audit_log(db, actor=payment.user, action="referral.qualified_purchase_reward", table_name="payments", record_id=payment.id, new_value={"reward_days": 7})
    db.flush()
    return "applied"


def validate_payment_evidence(payment: Payment, data: dict) -> str | None:
    amount = data.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount != int(payment.amount * 100):
        return "amount_mismatch"
    if data.get("currency") != payment.currency or data.get("status") != "success":
        return "currency_or_status_mismatch"
    customer = data.get("customer")
    email = customer.get("email") if isinstance(customer, dict) else None
    expected_email = payment.expected_customer_email or payment.user.email
    if not isinstance(email, str) or email.lower().strip() != expected_email.lower().strip():
        return "customer_mismatch"
    expected_environment = payment.provider_environment or provider_environment(get_settings().paystack_secret_key)
    if not expected_environment or data.get("domain") != expected_environment:
        return "environment_mismatch"
    provider_id = data.get("id")
    if isinstance(provider_id, bool) or not isinstance(provider_id, (int, str)) or not str(provider_id).isdigit() or int(provider_id) <= 0 or len(str(provider_id)) > 100:
        return "invalid_provider_transaction"
    metadata = data.get("metadata")
    if isinstance(metadata, dict) and "priceyard_user_id" in metadata and str(metadata["priceyard_user_id"]) != str(payment.user_id):
        return "account_binding_mismatch"
    return None


def get_payment_status(db: Session, reference: str, user: User) -> Payment:
    payment = db.scalar(select(Payment).where(Payment.reference == reference))
    if payment is None or (payment.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


def list_payments(db: Session, *, offset: int = 0, limit: int = 100) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.created_at.desc(), Payment.id.desc()).offset(offset).limit(limit)).all())
