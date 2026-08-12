"""Stage 4 owner smoke test against the configured PostgreSQL database.

Run from backend/: python ../docs/evidence/stage-4-owner-smoke.py
The script creates one temporary user, exercises the approved auth APIs,
and deletes that user before exit.
"""
from __future__ import annotations

import json
import os
import sys
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
from app.models.user import User  # noqa: E402

client = TestClient(app)
email = f"stage4-{uuid4().hex}@example.com"
password = "Stage4LocalTest!2026"
report: dict[str, str] = {}
user_id: int | None = None


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    report[label] = "PASS"


try:
    register = client.post(
        "/auth/register",
        json={
            "full_name": "Stage 4 Verification User",
            "email": email,
            "phone": None,
            "password": password,
        },
    )
    if register.status_code != 201:
        print("REGISTER STATUS:", register.status_code)
        print("REGISTER BODY:", register.text)
    expect(register.status_code == 201, "registration works")
    body = register.json()
    user_id = body["id"]
    expect(body["role"] == "free_user", "registration assigns free_user role")
    expect("password_hash" not in body and "password" not in body, "password hash not returned")

    with get_session_factory()() as db:
        db_user = db.scalar(select(User).where(User.id == user_id))
        expect(db_user is not None, "registered user persisted")
        expect(db_user.password_hash != password, "password is hashed")
        expect(db_user.password_hash.startswith("$2"), "bcrypt hash stored")

    duplicate = client.post(
        "/auth/register",
        json={
            "full_name": "Duplicate",
            "email": email,
            "phone": None,
            "password": password,
        },
    )
    expect(duplicate.status_code == 409, "duplicate email rejected")

    wrong = client.post("/auth/login", json={"email": email, "password": "wrong-password"})
    expect(wrong.status_code == 401, "wrong password rejected")

    login = client.post("/auth/login", json={"email": email, "password": password})
    expect(login.status_code == 200, "login works")
    token = login.json()["access_token"]
    expect(bool(token), "JWT generated")

    missing = client.get("/auth/me")
    expect(missing.status_code == 401, "missing JWT rejected")

    invalid = client.get("/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt"})
    expect(invalid.status_code == 401, "invalid JWT rejected")

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    expect(me.status_code == 200, "auth me works")
    expect(me.json()["email"] == email, "JWT resolves current user")
    expect("password_hash" not in me.json(), "auth me hides password hash")

    with get_session_factory()() as db:
        db_user = db.get(User, user_id)
        db_user.is_active = False
        db.commit()

    inactive_login = client.post("/auth/login", json={"email": email, "password": password})
    expect(inactive_login.status_code == 403, "inactive user login blocked")

    inactive_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    expect(inactive_me.status_code == 403, "inactive user protected access blocked")

    print(json.dumps(report, indent=2))
    print("STAGE 4 OWNER SMOKE: PASS")
finally:
    if user_id is not None:
        with get_session_factory()() as db:
            db_user = db.get(User, user_id)
            if db_user is not None:
                db.delete(db_user)
                db.commit()
