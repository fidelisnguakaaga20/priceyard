"""Remove the temporary Stage 19 browser admin created by stage-19-browser-admin.py."""
from __future__ import annotations
import os
import sys
from pathlib import Path
from sqlalchemy import select
BACKEND = Path(__file__).resolve().parents[2] / "backend"
if not (BACKEND / ".env").exists():
    raise SystemExit("FAIL: backend/.env is missing. Copy it from the previous stage first.")
os.chdir(BACKEND)
if str(BACKEND) not in sys.path: sys.path.insert(0, str(BACKEND))
from app.database import get_session_factory
from app.models.audit_log import AuditLog
from app.models.subscription import Subscription
from app.models.user import User

if len(sys.argv) != 2 or not sys.argv[1].startswith("stage19-browser-admin-") or not sys.argv[1].endswith("@example.com"):
    raise SystemExit("Usage: python docs/evidence/stage-19-browser-admin-cleanup.py stage19-browser-admin-...@example.com")
email = sys.argv[1].lower()
SessionLocal = get_session_factory()
with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        print("Temporary Stage 19 admin not found; nothing to clean.")
        raise SystemExit(0)
    for log in list(db.scalars(select(AuditLog).where(AuditLog.user_id == user.id)).all()): db.delete(log)
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if sub is not None: db.delete(sub)
    db.delete(user); db.commit()
    print("STAGE 19 TEMP ADMIN CLEANUP: PASS")
