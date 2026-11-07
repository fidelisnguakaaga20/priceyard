import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.user import User
from app.security import create_access_token
from app.services.subscription_service import build_trial_subscription


class AlertTestLinkTests(unittest.TestCase):
    """Temporary owner-approved test link: admins only, and it fails on purpose."""

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(full_name="Synthetic user", email="alert-user@example.com", password_hash="x",
                        role="free_user", is_active=True, referral_code="ALERTUSR")
            user.subscription = build_trial_subscription(user=user)
            admin = User(full_name="Synthetic admin", email="alert-admin@example.com", password_hash="x",
                         role="admin", is_active=True, referral_code="ALERTADM")
            db.add_all([user, admin])
            db.commit()
            self.user_id, self.admin_id = user.id, admin.id

        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def get(self, user_id=None):
        headers = {"Authorization": "Bearer " + create_access_token(user_id=user_id)} if user_id else {}
        return self.client.get("/admin/test-alert", headers=headers)

    def test_visitors_and_normal_users_cannot_use_it(self):
        self.assertEqual(self.get().status_code, 401)
        self.assertEqual(self.get(self.user_id).status_code, 403)

    def test_admin_triggers_one_deliberate_error(self):
        self.assertEqual(self.get(self.admin_id).status_code, 500)


if __name__ == "__main__":
    unittest.main()
