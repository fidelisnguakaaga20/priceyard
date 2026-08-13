"""Create a temporary Stage 19 admin account for manual browser rendering checks."""
from __future__ import annotations
import sys
from pathlib import Path
from uuid import uuid4
BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path: sys.path.insert(0, str(BACKEND))
from app.database import get_session_factory
from app.models.user import User
from app.utils.password import hash_password

password = "Stage19-Browser-Check!"
email = f"stage19-browser-admin-{uuid4().hex[:10]}@example.com"
SessionLocal = get_session_factory()
with SessionLocal() as db:
    user = User(full_name="Stage 19 Browser Admin", email=email, password_hash=hash_password(password), role="admin", is_active=True)
    db.add(user); db.commit(); db.refresh(user)
    print("STAGE 19 TEMP ADMIN CREATED")
    print(f"EMAIL: {email}")
    print(f"PASSWORD: {password}")
    print(f"USER ID: {user.id}")
    print("After the manual browser check, clean it up with:")
    print(f"python docs/evidence/stage-19-browser-admin-cleanup.py {email}")
