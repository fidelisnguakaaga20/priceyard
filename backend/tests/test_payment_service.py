"""Synthetic payment tests, executed through the isolated test bootstrap."""
import hashlib
import hmac
import json
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
import app.models  # noqa: F401
from app.models.entitlement_grant import EntitlementGrant
from app.models.payment import Payment
from app.models.referral_reward import ReferralReward
from app.models.subscription import Subscription
from app.models.user import User
from app.services import payment_service, subscription_service
from app.services.subscription_service import (
    activate_paid_subscription, apply_paid_expiry, aware_utc, build_trial_subscription,
    has_full_access, list_subscriptions, paid_cutoff, update_subscription_status,
)

NOW = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)


class FakeSettings:
    paystack_secret_key = "sk_test_synthetic_not_a_real_key"
    frontend_url = "http://localhost:4173"


class PaymentServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = self.make_user("payer")
        self.db.commit()
        self.patches = [patch.object(payment_service, "get_settings", return_value=FakeSettings()),
                        patch.object(payment_service, "utc_now", return_value=NOW),
                        patch.object(subscription_service, "utc_now", return_value=NOW)]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.db.close()
        self.engine.dispose()

    def make_user(self, name, *, verified=True, role="free_user"):
        user = User(full_name=f"Synthetic {name}", email=f"{name}@fixture.test",
                    password_hash="synthetic-not-used-for-login", role=role, is_active=True,
                    referral_code=name[:12].upper(), email_verified=verified)
        user.subscription = build_trial_subscription(user=user, now=NOW)
        self.db.add(user)
        self.db.flush()
        return user

    def make_payment(self, *, reference="py_synthetic", plan="monthly", user=None, status="pending"):
        user = user or self.user
        payment = Payment(user_id=user.id, reference=reference, plan=plan,
                          amount=Decimal("6000.00") if plan == "seasonal" else Decimal("2500.00"),
                          currency="NGN", status=status, expected_customer_email=user.email,
                          provider_environment="test")
        self.db.add(payment)
        self.db.commit()
        return payment

    def payload(self, payment, *, transaction_id=999):
        return {"event": "charge.success", "data": {
            "reference": payment.reference, "id": transaction_id,
            "amount": int(payment.amount * 100), "currency": "NGN", "status": "success",
            "domain": "test", "customer": {"email": payment.user.email},
            "metadata": {"priceyard_user_id": payment.user_id}}}

    def apply(self, payment, **kwargs):
        outcome = payment_service.handle_webhook_event(self.db, self.payload(payment, **kwargs))
        self.db.commit()
        return outcome

    def test_signature_verifies_exact_raw_payload(self):
        raw = json.dumps(self.payload(self.make_payment())).encode()
        signature = hmac.new(FakeSettings.paystack_secret_key.encode(), raw, hashlib.sha512).hexdigest()
        self.assertTrue(payment_service.verify_webhook_signature(raw, signature))
        self.assertFalse(payment_service.verify_webhook_signature(raw + b" ", signature))
        self.assertFalse(payment_service.verify_webhook_signature(raw, None))
        self.assertFalse(payment_service.verify_webhook_signature(raw, "\u00e9" * 128))

    def test_checkout_intent_is_durable_before_provider_call_and_snapshots_plan(self):
        def initialize(_url, **arguments):
            reference = arguments["json"]["reference"]
            with Session(self.engine) as observer:
                saved = observer.scalar(select(Payment).where(Payment.reference == reference))
                self.assertEqual(saved.status, "pending")
                self.assertEqual(saved.duration_days, 90)
                self.assertEqual(saved.amount, Decimal("6000.00"))
                self.assertEqual(saved.expected_customer_email, self.user.email)
                self.assertFalse(saved.access_applied)
            self.assertFalse(arguments["allow_redirects"])
            self.assertEqual(arguments["json"]["amount"], 600000)
            return Mock(ok=True, json=lambda: {"status": True, "data": {
                "authorization_url": "https://checkout.paystack.com/synthetic", "reference": reference}})
        with patch.object(payment_service.requests, "post", side_effect=initialize):
            result = payment_service.initiate_payment(self.db, self.user, "seasonal")
        self.assertTrue(result.reference.startswith("py_"))
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 0)

    def test_checkout_provider_timeout_keeps_reconcilable_pending_reference(self):
        with patch.object(payment_service.requests, "post", side_effect=payment_service.requests.Timeout):
            with self.assertRaises(HTTPException) as caught:
                payment_service.initiate_payment(self.db, self.user, "monthly")
        self.assertEqual(caught.exception.status_code, 502)
        self.db.rollback()  # same failure path as the HTTP transaction middleware
        with Session(self.engine) as observer:
            saved = observer.scalar(select(Payment))
            self.assertIsNotNone(saved)
            self.assertEqual(saved.status, "pending")
            self.assertFalse(saved.access_applied)

    def test_checkout_does_not_contact_provider_if_intent_commit_fails(self):
        with patch.object(Session, "commit", side_effect=RuntimeError("Synthetic unavailable database")):
            with patch.object(payment_service.requests, "post") as provider:
                with self.assertRaises(RuntimeError):
                    payment_service.initiate_payment(self.db, self.user, "monthly")
                provider.assert_not_called()
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count(Payment.id))), 0)

    def test_checkout_rejects_unbound_or_unsafe_provider_urls(self):
        invalid = ["https://checkout.paystack.com:8443/synthetic", "https://user@checkout.paystack.com/synthetic", "https://checkout.paystack.com/#fragment", "https://checkout.paystack.com:invalid/synthetic", "https://fixture.invalid/checkout"]
        for url in invalid:
            with self.subTest(url=url):
                def initialize(_url, **arguments):
                    return Mock(ok=True, json=lambda: {"status": True, "data": {"authorization_url": url, "reference": arguments["json"]["reference"]}})
                with patch.object(payment_service.requests, "post", side_effect=initialize):
                    with self.assertRaises(HTTPException):
                        payment_service.initiate_payment(self.db, self.user, "monthly")
                self.db.rollback()
        with patch.object(payment_service.requests, "post", return_value=Mock(ok=True, json=lambda: {"status": True, "data": {"authorization_url": "https://checkout.paystack.com/synthetic", "reference": "different-reference"}})):
            with self.assertRaises(HTTPException):
                payment_service.initiate_payment(self.db, self.user, "monthly")

    def test_manual_grant_never_starts_an_unnecessary_checkout(self):
        self.user.subscription.status = "active"
        self.user.subscription.manual_grant = True
        self.db.commit()
        with patch.object(payment_service.requests, "post") as provider:
            with self.assertRaises(HTTPException) as caught:
                payment_service.initiate_payment(self.db, self.user, "monthly")
            self.assertEqual(caught.exception.status_code, 409)
            provider.assert_not_called()
        self.user.subscription.manual_grant = False
        self.user.subscription.status = "trial"
        self.user.role = "admin"
        self.db.commit()
        with patch.object(payment_service.requests, "post") as provider:
            with self.assertRaises(HTTPException) as caught:
                payment_service.initiate_payment(self.db, self.user, "monthly")
            self.assertEqual(caught.exception.status_code, 409)
            provider.assert_not_called()

    def test_success_preserves_trial_then_adds_duration(self):
        payment = self.make_payment()
        trial_end = aware_utc(self.user.subscription.trial_ends_at)
        self.assertEqual(self.apply(payment), "applied")
        self.assertEqual(payment.status, "success")
        self.assertEqual(payment.paystack_transaction_id, "999")
        self.assertEqual(paid_cutoff(self.user.subscription), trial_end + timedelta(days=30))
        self.assertTrue(payment.access_applied)
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 1)
        self.assertEqual(self.user.role, "free_user")

    def test_distinct_purchases_preserve_all_unused_time(self):
        first = self.make_payment(reference="py_first", plan="seasonal")
        second = self.make_payment(reference="py_second")
        trial_end = aware_utc(self.user.subscription.trial_ends_at)
        self.apply(first, transaction_id=1001)
        self.apply(second, transaction_id=1002)
        self.assertEqual(paid_cutoff(self.user.subscription), trial_end + timedelta(days=120))

    def test_replay_does_not_duplicate(self):
        payment = self.make_payment(plan="seasonal")
        self.apply(payment)
        cutoff = paid_cutoff(self.user.subscription)
        self.assertEqual(self.apply(payment), "already_applied")
        self.assertEqual(paid_cutoff(self.user.subscription), cutoff)
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 1)

    def test_reverse_plan_order_has_same_total_value(self):
        first = self.make_payment(reference="py_first")
        second = self.make_payment(reference="py_second", plan="seasonal")
        trial_end = aware_utc(self.user.subscription.trial_ends_at)
        self.apply(first, transaction_id=1001)
        self.apply(second, transaction_id=1002)
        self.assertEqual(paid_cutoff(self.user.subscription), trial_end + timedelta(days=120))

    def test_invalid_evidence_grants_nothing(self):
        cases = [("amount", 249999), ("currency", "USD"), ("status", "failed"),
                 ("domain", "live"), ("id", True), ("customer", {"email": "other@fixture.test"}),
                 ("metadata", {"priceyard_user_id": 99999})]
        for index, (field, value) in enumerate(cases):
            with self.subTest(field=field):
                payment = self.make_payment(reference=f"py_mismatch_{index}")
                payload = self.payload(payment)
                payload["data"][field] = value
                self.assertEqual(payment_service.handle_webhook_event(self.db, payload), "evidence_mismatch")
                self.db.commit()
                self.assertFalse(payment.access_applied)
                self.assertEqual(payment.status, "pending")
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 0)

    def test_transaction_id_cannot_apply_to_other_purchase(self):
        first = self.make_payment(reference="py_original")
        second = self.make_payment(reference="py_duplicate")
        self.apply(first)
        self.assertEqual(self.apply(second), "evidence_mismatch")
        self.assertFalse(second.access_applied)

    def test_failure_before_activation_rolls_back_and_retries(self):
        payment = self.make_payment()
        with patch.object(payment_service, "activate_paid_subscription", side_effect=RuntimeError("synthetic crash")):
            with self.assertRaises(RuntimeError):
                payment_service.handle_webhook_event(self.db, self.payload(payment))
        self.db.rollback()
        self.db.refresh(payment)
        self.assertEqual(payment.status, "pending")
        self.assertIsNone(payment.confirmed_at)
        self.assertEqual(self.apply(payment), "applied")

    def test_audit_failure_rolls_back_grant_and_subscription(self):
        payment = self.make_payment()
        previous_end = aware_utc(self.user.subscription.trial_ends_at)
        with patch.object(payment_service, "create_audit_log", side_effect=RuntimeError("synthetic audit failure")):
            with self.assertRaises(RuntimeError):
                payment_service.handle_webhook_event(self.db, self.payload(payment))
        self.db.rollback()
        self.db.refresh(payment)
        self.assertFalse(payment.access_applied)
        self.assertEqual(self.user.subscription.status, "trial")
        self.assertEqual(aware_utc(self.user.subscription.trial_ends_at), previous_end)
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 0)

    def test_missing_subscription_created_safely(self):
        payment = self.make_payment()
        self.db.delete(self.user.subscription)
        self.db.commit()
        self.assertEqual(self.apply(payment), "applied")
        sub = self.db.scalar(select(Subscription).where(Subscription.user_id == self.user.id))
        self.assertEqual(paid_cutoff(sub), NOW + timedelta(days=30))

    def test_legacy_success_requires_review(self):
        payment = self.make_payment(status="success")
        payment.requires_reconciliation = True
        self.db.commit()
        self.assertEqual(self.apply(payment), "review_required")
        self.assertFalse(payment.access_applied)
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 0)

    def test_legacy_acknowledgement_does_not_invent_grant(self):
        admin = self.make_user("admin", role="admin")
        payment = self.make_payment(status="success")
        payment.requires_reconciliation = True
        self.db.commit()
        result = payment_service.handle_webhook_event(self.db, self.payload(payment), actor=admin,
            legacy_resolution="already_applied", reason="Synthetic reviewed access evidence")
        self.db.commit()
        self.assertEqual(result, "already_applied")
        self.assertTrue(payment.access_applied)
        self.assertIsNone(payment.entitlement_applied_at)
        self.assertEqual(self.db.scalar(select(func.count(EntitlementGrant.id))), 0)

    def test_legacy_cutoff_keeps_entire_end_day(self):
        sub = self.user.subscription
        sub.status = "active"
        sub.end_date = NOW.date() + timedelta(days=10)
        previous_cutoff = paid_cutoff(sub)
        self.assertEqual(previous_cutoff.date(), NOW.date() + timedelta(days=11))
        self.apply(self.make_payment())
        self.assertEqual(paid_cutoff(sub), previous_cutoff + timedelta(days=30))

    def test_manual_grant_survives_existing_checkout(self):
        payment = self.make_payment()
        sub = update_subscription_status(self.db, self.user.subscription, "active")
        self.db.commit()
        self.apply(payment)
        self.assertTrue(sub.manual_grant)
        self.assertIsNone(sub.paid_expires_at)
        self.assertTrue(has_full_access(sub, now=NOW + timedelta(days=10000)))
        self.assertEqual(self.db.scalar(select(EntitlementGrant.disposition)), "manual_grant_preserved")

    def test_cancel_preserves_purchased_access(self):
        self.apply(self.make_payment())
        sub = self.user.subscription
        cutoff = paid_cutoff(sub)
        update_subscription_status(self.db, sub, "cancelled")
        self.assertTrue(has_full_access(sub, now=NOW))
        self.assertEqual(paid_cutoff(sub), cutoff)
        self.assertIsNotNone(sub.cancellation_requested_at)
        self.assertFalse(has_full_access(sub, now=cutoff))
        with self.assertRaises(HTTPException):
            update_subscription_status(self.db, sub, "free")

    def test_all_expired_rows_processed_without_removing_reporter(self):
        reporter = self.make_user("reporter", role="reporter")
        for user in (self.user, reporter):
            user.subscription.status = "active"
            user.subscription.end_date = NOW.date() - timedelta(days=1)
        self.db.commit()
        list_subscriptions(self.db)
        self.assertEqual(self.user.subscription.status, "expired")
        self.assertEqual(reporter.subscription.status, "expired")
        self.assertEqual(reporter.role, "reporter")

    def test_expiry_exact_boundary(self):
        sub = self.user.subscription
        activate_paid_subscription(self.db, sub, plan="monthly", now=NOW)
        cutoff = paid_cutoff(sub)
        self.assertFalse(apply_paid_expiry(sub, now=cutoff - timedelta(microseconds=1)))
        self.assertTrue(apply_paid_expiry(sub, now=cutoff))

    def test_payment_status_ownership(self):
        payment = self.make_payment()
        other = self.make_user("other")
        self.assertEqual(payment_service.get_payment_status(self.db, payment.reference, self.user).id, payment.id)
        with self.assertRaises(HTTPException) as error:
            payment_service.get_payment_status(self.db, payment.reference, other)
        self.assertEqual(error.exception.status_code, 404)

    def test_unknown_reference_classified(self):
        payload = self.payload(self.make_payment())
        payload["data"]["reference"] = "py_unknown"
        self.assertEqual(payment_service.handle_webhook_event(self.db, payload), "unknown_reference")

    def test_verified_first_purchase_rewards_once(self):
        referrer = self.make_user("referrer")
        self.user.referred_by_id = referrer.id
        previous_end = aware_utc(referrer.subscription.trial_ends_at)
        first = self.make_payment()
        self.apply(first)
        self.assertEqual(aware_utc(referrer.subscription.trial_ends_at), previous_end + timedelta(days=7))
        self.apply(first)
        self.apply(self.make_payment(reference="py_second"), transaction_id=1000)
        self.assertEqual(self.db.scalar(select(func.count(ReferralReward.id))), 1)

    def test_unverified_purchase_rewards_nothing(self):
        referrer = self.make_user("referrer")
        self.user.referred_by_id = referrer.id
        self.user.email_verified = False
        self.apply(self.make_payment())
        self.assertEqual(self.db.scalar(select(func.count(ReferralReward.id))), 0)

    def test_four_award_cap_preserves_existing_earned_days(self):
        referrer = self.make_user("referrer")
        referrer.subscription.trial_ends_at += timedelta(days=21)
        previous_end = aware_utc(referrer.subscription.trial_ends_at)
        for index in range(6):
            user = self.make_user(f"referred{index}")
            user.referred_by_id = referrer.id
            payment = self.make_payment(reference=f"py_reward_{index}", user=user)
            self.apply(payment, transaction_id=1000 + index)
        self.assertEqual(self.db.scalar(select(func.count(ReferralReward.id))), 4)
        self.assertEqual(aware_utc(referrer.subscription.trial_ends_at), previous_end + timedelta(days=28))


if __name__ == "__main__":
    unittest.main()
