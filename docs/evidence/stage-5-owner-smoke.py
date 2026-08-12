"""Stage 5 owner smoke test against the configured PostgreSQL database.

Run from backend/: python ../docs/evidence/stage-5-owner-smoke.py
Creates temporary normal/admin users, exercises the approved subscription/trial
behavior, and deletes the temporary users before exit.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.database import get_session_factory  # noqa: E402
from app.main import app  # noqa: E402
from app.models.subscription import Subscription  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.subscription_service import TRIAL_DURATION_DAYS, has_full_access, utc_now  # noqa: E402
from app.utils.password import hash_password  # noqa: E402

client = TestClient(app)
user_email = f"stage5-user-{uuid4().hex}@example.com"
admin_email = f"stage5-admin-{uuid4().hex}@example.com"
password = "Stage5LocalTest!2026"
report: dict[str, str] = {}
user_id: int | None = None
admin_id: int | None = None


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    report[label] = "PASS"


def login(email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    if response.status_code != 200:
        print("LOGIN STATUS:", response.status_code, response.text)
    expect(response.status_code == 200, f"login works for {email}")
    return response.json()["access_token"]


try:
    register = client.post(
        "/auth/register",
        json={
            "full_name": "Stage 5 Trial User",
            "email": user_email,
            "phone": None,
            "password": password,
        },
    )
    if register.status_code != 201:
        print("REGISTER STATUS:", register.status_code, register.text)
    expect(register.status_code == 201, "new user registration works")
    user_id = register.json()["id"]

    with get_session_factory()() as db:
        user = db.get(User, user_id)
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
        expect(subscription is not None, "new user receives subscription")
        expect(subscription.status == "trial", "new user starts on trial")
        expect(subscription.trial_started_at is not None, "trial start recorded")
        expect(subscription.trial_ends_at is not None, "trial end recorded")
        duration = subscription.trial_ends_at - subscription.trial_started_at
        expect(duration == timedelta(days=TRIAL_DURATION_DAYS), "trial lasts exactly 14 days")
        expect(has_full_access(subscription), "active trial has full access")

        admin = User(
            full_name="Stage 5 Admin",
            email=admin_email,
            phone=None,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_id = admin.id

    user_token = login(user_email)
    admin_token = login(admin_email)

    own = client.get(f"/subscriptions/{user_id}", headers={"Authorization": f"Bearer {user_token}"})
    expect(own.status_code == 200, "user can view own subscription")
    expect(own.json()["status"] == "trial", "subscription API returns trial status")

    invalid = client.patch(
        f"/subscriptions/{user_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "invalid"},
    )
    expect(invalid.status_code == 422, "invalid status rejected")

    non_admin_update = client.patch(
        f"/subscriptions/{user_id}/status",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"status": "active"},
    )
    expect(non_admin_update.status_code == 403, "non-admin subscription update blocked")

    for target_status, expected_full in [
        ("active", True),
        ("free", False),
        ("cancelled", False),
        ("trial", True),
    ]:
        changed = client.patch(
            f"/subscriptions/{user_id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": target_status},
        )
        expect(changed.status_code == 200, f"admin can set {target_status} status")
        with get_session_factory()() as db:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            expect(has_full_access(subscription) is expected_full, f"{target_status} access classification is correct")
            if target_status == "active":
                expect(subscription.user.role == "paid_user", "active paid status assigns paid_user role")
            elif target_status in {"free", "cancelled", "trial"}:
                expect(subscription.user.role == "free_user", f"{target_status} keeps/returns free_user role")

    with get_session_factory()() as db:
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
        subscription.status = "trial"
        subscription.trial_started_at = utc_now() - timedelta(days=15)
        subscription.trial_ends_at = utc_now() - timedelta(days=1)
        db.commit()

    expired = client.get(f"/subscriptions/{user_id}", headers={"Authorization": f"Bearer {user_token}"})
    expect(expired.status_code == 200, "expired trial subscription can still be viewed")
    expect(expired.json()["status"] == "expired", "expired trial changes to expired status")
    with get_session_factory()() as db:
        subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
        expect(not has_full_access(subscription), "expired trial has limited access")
        expect(subscription.user.role == "free_user", "expired trial returns to free_user role")

    listing = client.get("/subscriptions", headers={"Authorization": f"Bearer {admin_token}"})
    expect(listing.status_code == 200, "admin can list subscriptions")
    expect(any(item["user_id"] == user_id for item in listing.json()), "admin list contains trial user")

finally:
    with get_session_factory()() as db:
        for cleanup_id in [user_id, admin_id]:
            if cleanup_id is not None:
                subscription = db.scalar(select(Subscription).where(Subscription.user_id == cleanup_id))
                if subscription is not None:
                    db.delete(subscription)
                    db.flush()
                user = db.get(User, cleanup_id)
                if user is not None:
                    db.delete(user)
        db.commit()

print(json.dumps(report, indent=2))
print("STAGE 5 OWNER SMOKE: PASS")
