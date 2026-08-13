"""Stage 19 owner verification helper.

Run from the project root after copying backend/.env into this stage.
It performs a real npm production build, verifies the Stage 19 source/route contract,
and checks the existing admin APIs against the owner's configured PostgreSQL database.
No Stage 20 behavior is added or tested here.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# app.config intentionally reads `.env` relative to the current working
# directory. Owner smoke tests are launched from the project root, while the
# approved runtime environment file lives at backend/.env. Enter the backend
# directory before importing app modules so the real owner configuration is
# loaded exactly as it is when Uvicorn is started from backend/.
os.chdir(BACKEND)

from fastapi.testclient import TestClient
from sqlalchemy import select
from app.database import get_session_factory
from app.main import app
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
checks: dict[str, str] = {}
run_id = uuid4().hex
password = "Stage19-Test-Password!"
admin_email = f"stage19-admin-{run_id}@example.com"
user_email = f"stage19-user-{run_id}@example.com"
admin_id: int | None = None
user_id: int | None = None


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    check(f"login works for {email}", response.status_code == 200)
    return response.json()["access_token"]


def run(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


try:
    if not (BACKEND / ".env").exists():
        raise SystemExit("FAIL: backend/.env is missing. Copy it from Stage 18 first.")
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not shutil.which(npm):
        raise SystemExit("FAIL: npm is not available.")

    run([sys.executable, str(ROOT / "docs" / "evidence" / "stage-19-static-check.py")], ROOT)
    run([npm, "install"], FRONTEND)
    run([npm, "run", "build"], FRONTEND)
    check("frontend production build exists", (FRONTEND / "dist" / "index.html").exists())

    with SessionLocal() as db:
        admin = User(full_name="Stage 19 Admin", email=admin_email, password_hash=hash_password(password), role="admin", is_active=True)
        db.add(admin); db.commit(); db.refresh(admin); admin_id = admin.id

    response = client.post("/auth/register", json={"full_name": "Stage 19 User", "email": user_email, "password": password})
    check("normal user registration works", response.status_code == 201)
    user_id = response.json()["id"]
    admin_token = login(admin_email)
    user_token = login(user_email)

    check("ordinary user cannot access admin users API", client.get("/users", headers=auth(user_token)).status_code == 403)
    check("ordinary user cannot access audit logs", client.get("/audit-logs", headers=auth(user_token)).status_code == 403)

    admin_reads = [
        "/users", "/commodities", "/markets", "/price-updates", "/price-updates/history",
        "/market-signals", "/quality-signals", "/buying-zones", "/sell-watch-windows",
        "/storage-suitability", "/cost-breakdowns", "/faq", "/subscriptions",
        "/feedback", "/feedback/summary", "/audit-logs", "/reports/prices.csv",
    ]
    for endpoint in admin_reads:
        response = client.get(endpoint, headers=auth(admin_token))
        check(f"admin data source works: {endpoint}", response.status_code == 200)

    print(checks)
    print("STAGE 19 OWNER SMOKE: PASS")
    print("MANUAL OWNER CHECK: log in as an admin account and confirm the Admin link/dashboard plus one management form render normally before approval.")
finally:
    with SessionLocal() as db:
        if admin_id is not None:
            for item in list(db.scalars(select(AuditLog).where(AuditLog.user_id == admin_id)).all()):
                db.delete(item)
            db.commit()
            admin = db.get(User, admin_id)
            if admin is not None:
                db.delete(admin)
            db.commit()
        if user_id is not None:
            sub = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            if sub is not None:
                db.delete(sub)
            user = db.get(User, user_id)
            if user is not None:
                db.delete(user)
            db.commit()
