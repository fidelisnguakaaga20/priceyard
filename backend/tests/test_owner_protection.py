"""Synthetic API proofs for derived Owner authority; no production configuration."""
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import jwt
from fastapi import HTTPException
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User
from app.security import create_access_token
from app.services.subscription_service import build_trial_subscription


class OwnerProtectionTests(unittest.TestCase):
    def setUp(self):
        self.owner_config = patch.object(get_settings(), "owner_email", "founder@example.com")
        self.owner_config.start()
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.ids = {}
        with Session(self.engine) as db:
            for label, role in (("founder", "admin"), ("staff", "admin"),
                                ("other-admin", "admin"), ("member", "free_user"),
                                ("reporter", "reporter")):
                user = User(full_name="Synthetic " + label, email=label + "@example.com",
                            password_hash="synthetic-unchanged-hash", role=role,
                            is_active=True, referral_code="OWNERTEST" + str(len(self.ids)))
                user.subscription = build_trial_subscription(user=user)
                if label == "founder":
                    user.subscription.status = "expired"
                    user.subscription.trial_ends_at = datetime.now(timezone.utc) - timedelta(days=30)
                db.add(user)
                db.flush()
                self.ids[label] = user.id
            db.commit()

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)
        self.headers = {name: {"Authorization": "Bearer " + create_access_token(user_id=user_id)}
                        for name, user_id in self.ids.items()}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        self.owner_config.stop()

    def state(self):
        with Session(self.engine) as db:
            return {
                "users": [(u.id, u.email, u.role, u.is_active, u.auth_version, u.password_hash)
                          for u in db.scalars(select(User).order_by(User.id))],
                "subscriptions": [(s.user_id, s.status, s.plan_name, s.start_date, s.end_date,
                                   s.trial_started_at, s.trial_ends_at, s.payment_reference)
                                  for s in db.scalars(select(Subscription).order_by(Subscription.id))],
                "audits": [(a.id, a.action, a.record_id)
                           for a in db.scalars(select(AuditLog).order_by(AuditLog.id))],
            }

    def denied(self, actor, target, payload, expected=403, headers=None):
        before = self.state()
        response = self.client.patch(f"/users/{self.ids[target]}", json=payload,
                                     headers=headers or self.headers[actor])
        self.assertEqual(response.status_code, expected, response.text)
        self.assertEqual(self.state(), before)
        return response

    def test_owner_metadata_and_expired_subscription_keep_full_access_without_rewriting_billing(self):
        before = self.state()
        owner = self.client.get("/auth/me", headers=self.headers["founder"])
        self.assertEqual(owner.status_code, 200, owner.text)
        self.assertTrue(owner.json()["is_owner"])
        self.assertEqual(owner.json()["role"], "admin")
        self.assertFalse(self.client.get("/auth/me", headers=self.headers["staff"]).json()["is_owner"])
        for path in ("/users/page", "/users"):
            response = self.client.get(path, headers=self.headers["founder"])
            self.assertEqual(response.status_code, 200, response.text)
            rows = response.json()["items"] if path.endswith("/page") else response.json()
            self.assertEqual([row["id"] for row in rows if row["is_owner"]], [self.ids["founder"]])
            self.assertTrue(all("password_hash" not in row and "auth_version" not in row for row in rows))
        history = self.client.get("/price-updates/history", headers=self.headers["founder"])
        self.assertEqual(history.status_code, 200, history.text)
        self.assertEqual(self.state(), before)

    def test_other_admin_cannot_demote_deactivate_or_even_resubmit_owner_authority(self):
        for payload in ({"role": "free_user"}, {"role": "reporter"}, {"is_active": False},
                        {"role": "admin"}, {"is_active": True}):
            with self.subTest(payload=payload):
                self.denied("staff", "founder", payload)

    def test_owner_cannot_demote_or_deactivate_self(self):
        for payload in ({"is_active": False}, {"role": "free_user"}, {"role": "reporter"},
                        {"role": "paid_user", "is_active": False}):
            with self.subTest(payload=payload):
                self.denied("founder", "founder", payload, 409)

    def test_only_owner_can_appoint_or_manage_any_admin_including_self_and_inactive_admin(self):
        for actor, target, payload in (
            ("staff", "member", {"role": "admin"}),
            ("staff", "other-admin", {"role": "reporter"}),
            ("staff", "other-admin", {"is_active": False}),
            ("staff", "staff", {"role": "reporter"}),
            ("staff", "staff", {"is_active": False}),
        ):
            with self.subTest(target=target, payload=payload):
                self.denied(actor, target, payload)
        with Session(self.engine) as db:
            db.get(User, self.ids["other-admin"]).is_active = False
            db.commit()
        self.denied("staff", "other-admin", {"is_active": True})

    def test_owner_can_appoint_demote_disable_and_reactivate_staff_with_audits_and_revocation(self):
        original = self.state()["subscriptions"]
        for role in ("admin", "reporter"):
            response = self.client.patch(f"/users/{self.ids['member']}", json={"role": role},
                                         headers=self.headers["founder"])
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["role"], role)
            self.assertFalse(response.json()["is_owner"])
        self.assertEqual(self.state()["subscriptions"], original)
        for enabled in (False, True):
            response = self.client.patch(f"/users/{self.ids['staff']}", json={"is_active": enabled},
                                         headers=self.headers["founder"])
            self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers["staff"]).status_code, 401)
        with Session(self.engine) as db:
            staff = db.get(User, self.ids["staff"])
            self.assertEqual((staff.role, staff.is_active, staff.auth_version), ("admin", True, 1))
            self.assertEqual(len(db.scalars(select(AuditLog)).all()), 4)

    def test_regular_admin_keeps_normal_non_admin_management_and_subscription_rules(self):
        for role, status in (("paid_user", "active"), ("free_user", "free"), ("reporter", "free")):
            response = self.client.patch(f"/users/{self.ids['member']}", json={"role": role},
                                         headers=self.headers["staff"])
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["role"], role)
            with Session(self.engine) as db:
                subscription = db.get(User, self.ids["member"]).subscription
                self.assertEqual(subscription.status, status)
                self.assertIsNone(subscription.end_date)
        response = self.client.patch(f"/users/{self.ids['member']}", json={"is_active": False},
                                     headers=self.headers["staff"])
        self.assertEqual(response.status_code, 200, response.text)

    def test_forged_owner_payload_headers_and_signed_role_claim_do_not_grant_authority(self):
        self.denied("staff", "member", {"role": "admin", "is_owner": True})
        spoofed_headers = dict(self.headers["staff"], **{"X-Owner": "true", "X-Owner-Email": "founder@example.com"})
        self.denied("staff", "member", {"role": "admin"}, headers=spoofed_headers)
        settings = get_settings()
        claims = jwt.decode(self.headers["staff"]["Authorization"].split()[1], settings.jwt_secret,
                            algorithms=[settings.jwt_algorithm])
        claims.update(role="owner", is_owner=True, email="founder@example.com")
        spoofed = jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        self.denied("staff", "member", {"role": "admin"}, headers={"Authorization": "Bearer " + spoofed})
        self.denied("member", "member", {"role": "admin"})
        self.denied("founder", "member", {"role": "owner"}, 422)

    def test_matching_free_account_cannot_bootstrap_owner_and_public_registration_cannot_claim_role(self):
        with Session(self.engine) as db:
            db.get(User, self.ids["founder"]).role = "free_user"
            db.commit()
        profile = self.client.get("/auth/me", headers=self.headers["founder"])
        self.assertEqual(profile.status_code, 200)
        self.assertFalse(profile.json()["is_owner"])
        self.denied("founder", "member", {"role": "admin"})
        self.denied("staff", "founder", {"role": "admin"})
        with patch("app.routes.auth_routes.notify_admins", return_value=None):
            response = self.client.post("/auth/register", json={
                "full_name": "Synthetic new member", "email": "registration-owner-test@example.com",
                "password": "PriceYardDemo8!", "role": "admin", "is_owner": True,
            })
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["role"], "free_user")
        self.assertFalse(response.json()["is_owner"])

    def test_ambiguous_case_variant_owner_email_fails_closed_and_protected_row_stays_unchanged(self):
        with Session(self.engine) as db:
            duplicate = User(full_name="Synthetic legacy duplicate", email="FOUNDER@example.com",
                             password_hash="synthetic-only", role="admin", is_active=True,
                             referral_code="OWNERDUP")
            db.add(duplicate)
            db.commit()
        profile = self.client.get("/auth/me", headers=self.headers["founder"])
        self.assertFalse(profile.json()["is_owner"])
        self.denied("founder", "member", {"role": "admin"})
        self.denied("staff", "founder", {"is_active": False})

    def test_owner_grant_audit_failure_rolls_back_all_role_and_subscription_changes(self):
        before = self.state()
        with patch("app.routes.user_routes.create_audit_log", side_effect=RuntimeError("Synthetic audit failure")):
            response = self.client.patch(f"/users/{self.ids['member']}", json={"role": "admin"},
                                         headers=self.headers["founder"])
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.state(), before)
        self.assertTrue(self.client.get("/auth/me", headers=self.headers["founder"]).json()["is_owner"])

    def test_existing_admin_token_loses_admin_access_immediately_after_owner_demotion(self):
        # Keep the same token: browser/JWT role snapshots must not retain authority.
        headers = self.headers["staff"]
        self.assertEqual(self.client.get("/users/page", headers=headers).status_code, 200)
        response = self.client.patch(f"/users/{self.ids['staff']}", json={"role": "reporter"},
                                     headers=self.headers["founder"])
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/users/page", headers=headers).status_code, 403)
        profile = self.client.get("/auth/me", headers=headers)
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["role"], "reporter")
        self.assertFalse(profile.json()["is_owner"])
        before = self.state()
        denied = self.client.patch(f"/users/{self.ids['member']}", json={"is_active": False}, headers=headers)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.state(), before)

    def test_queued_actor_auth_version_is_rechecked_before_any_target_mutation(self):
        from app.schemas.user_schema import AdminUserUpdate
        from app.services.user_service import update_user

        before = self.state()
        with Session(self.engine) as db:
            actor = db.get(User, self.ids["staff"])
            captured_version = actor.auth_version
            db.execute(update(User).where(User.id == actor.id).values(auth_version=User.auth_version + 1))
            db.commit()
            target = db.get(User, self.ids["member"])
            with self.assertRaises(HTTPException) as denied:
                update_user(db, target, AdminUserUpdate(is_active=False), actor=actor,
                            actor_auth_version=captured_version)
            self.assertEqual(denied.exception.status_code, 403)
            db.rollback()
        after = self.state()
        self.assertEqual(after["subscriptions"], before["subscriptions"])
        self.assertEqual(after["audits"], before["audits"])
        self.assertEqual(next(row for row in after["users"] if row[0] == self.ids["member"]),
                         next(row for row in before["users"] if row[0] == self.ids["member"]))


def verify_owner_demotion_blocks_already_authenticated_staff(test, engine):
    """Exactly two API operations against the runner's pinned synthetic server."""
    import threading
    from app.routes import user_routes

    Base.metadata.create_all(engine)
    with Session(engine) as db:
        ids = {}
        for label, role in (("founder", "admin"), ("staff", "admin"), ("member", "free_user")):
            user = User(full_name="Synthetic PG " + label, email=label + "@owner-pg.example.com",
                        password_hash="synthetic-unused", role=role, is_active=True,
                        referral_code="OWNERPG" + str(len(ids)))
            user.subscription = build_trial_subscription(user=user)
            db.add(user)
            db.flush()
            ids[label] = user.id
        db.commit()

    def sessions():
        with Session(engine, expire_on_commit=False) as db:
            yield db
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = sessions
    held = threading.Event()
    waiting = threading.Event()
    release = threading.Event()
    outcomes = {}
    original_prepare = user_routes.prepare_user_update

    def interleave(db, user_id):
        if user_id == ids["member"]:
            # This is reached only after real bearer authentication saw Admin.
            waiting.set()
        prepared = original_prepare(db, user_id)
        if user_id == ids["staff"]:
            held.set()
            if not release.wait(8):
                raise RuntimeError("Synthetic owner interleave deadline exceeded")
        return prepared

    def worker(label, target, payload):
        try:
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.patch(f"/users/{ids[target]}", json=payload, headers={
                    "Authorization": "Bearer " + create_access_token(user_id=ids[label]),
                })
                outcomes[label] = response.status_code
        except BaseException as error:
            outcomes[label] = type(error).__name__

    threads = [threading.Thread(target=worker, args=("founder", "staff", {"role": "reporter"})),
               threading.Thread(target=worker, args=("staff", "member", {"is_active": False}))]
    try:
        with patch.object(get_settings(), "owner_email", "founder@owner-pg.example.com"), \
                patch.object(user_routes, "prepare_user_update", side_effect=interleave):
            threads[0].start()
            test.assertTrue(held.wait(8), "Owner did not acquire the existing transaction guard")
            threads[1].start()
            test.assertTrue(waiting.wait(8), "Staff did not reach the guard after authentication")
            release.set()
            for thread in threads:
                thread.join(15)
            test.assertFalse(any(thread.is_alive() for thread in threads))
            test.assertEqual(outcomes, {"founder": 200, "staff": 403})
            with Session(engine) as db:
                test.assertEqual(db.get(User, ids["staff"]).role, "reporter")
                member = db.get(User, ids["member"])
                test.assertEqual((member.role, member.is_active, member.auth_version), ("free_user", True, 0))
                test.assertEqual([a.action for a in db.scalars(select(AuditLog)).all()], ["user.update"])
                test.assertTrue(db.get(User, ids["founder"]).is_owner)
    finally:
        release.set()
        for thread in threads:
            if thread.ident is not None:
                thread.join(15)
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
