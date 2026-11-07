"""Per-account wrong-password pause: 5 wrong passwords in 15 minutes pauses that account."""
from datetime import datetime, timedelta, timezone
import hashlib
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models  # noqa: F401  (registers every table)
from app.main import app
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.rate_limit import limiter
from app.services import login_throttle
from app.utils.password import hash_password

PASSWORD = "SyntheticRightPassword8!"


class LoginThrottleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password(PASSWORD)

    def setUp(self):
        login_throttle.reset_all()
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            for index, email in enumerate(("target@example.com", "other@example.com")):
                db.add(User(full_name=f"Synthetic {index}", email=email, password_hash=self.password_hash,
                            role="free_user", referral_code=f"THROTTLE{index}"))
            db.commit()

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        login_throttle.reset_all()
        limiter.reset()

    def login(self, email="target@example.com", password="wrong-password"):
        limiter.reset()  # isolate from the separate per-address 5/minute limit
        return self.client.post("/auth/login", json={"email": email, "password": password})

    def test_fifth_wrong_password_pauses_account_even_for_right_password(self):
        for _ in range(5):
            self.assertEqual(self.login().status_code, 401)
        response = self.login(password=PASSWORD)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Too many wrong passwords", response.json()["detail"])
        self.assertIn("15 minutes", response.json()["detail"])
        self.assertTrue(0 < int(response.headers["Retry-After"]) <= login_throttle.LOCK_SECONDS)

    def test_other_accounts_are_not_affected(self):
        for _ in range(5):
            self.login()
        self.assertEqual(self.login(email="other@example.com", password=PASSWORD).status_code, 200)

    def test_email_case_and_spaces_count_as_same_account(self):
        for email in ("Target@Example.com", " target@example.com", "TARGET@EXAMPLE.COM", "target@example.com", "Target@example.COM"):
            self.client.post("/auth/login", json={"email": email.strip(), "password": "wrong"})
            limiter.reset()
        self.assertEqual(self.login(password=PASSWORD).status_code, 429)

    def test_successful_login_clears_earlier_failures(self):
        for _ in range(4):
            self.login()
        self.assertEqual(self.login(password=PASSWORD).status_code, 200)
        for _ in range(4):
            self.assertEqual(self.login().status_code, 401)
        self.assertEqual(self.login(password=PASSWORD).status_code, 200)

    def test_unknown_email_is_paused_the_same_way(self):
        for _ in range(5):
            self.assertEqual(self.login(email="nobody@example.com").status_code, 401)
        self.assertEqual(self.login(email="nobody@example.com").status_code, 429)

    def test_password_reset_ends_the_pause(self):
        for _ in range(5):
            self.login()
        raw = "synthetic-throttle-reset-token-0123456789abcdef"
        with Session(self.engine) as db:
            user_id = db.query(User.id).filter(User.email == "target@example.com").scalar()
            db.add(PasswordResetToken(user_id=user_id, token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                                      expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)))
            db.commit()
        reset = self.client.post("/auth/reset-password", json={"token": raw, "new_password": "BrandNewPassword9!"})
        self.assertEqual(reset.status_code, 200)
        self.assertEqual(self.login(password="BrandNewPassword9!").status_code, 200)

    def test_pause_and_failures_expire_with_time(self):
        start = 1_000_000.0
        for second in range(5):
            login_throttle.record_failure("clock@example.com", now=start + second)
        self.assertGreater(login_throttle.seconds_locked("clock@example.com", now=start + 10), 0)
        self.assertEqual(login_throttle.seconds_locked("clock@example.com", now=start + 4 + login_throttle.LOCK_SECONDS), 0)
        # Failures spread wider than the 15-minute window never add up to a pause.
        for step in range(5):
            login_throttle.record_failure("spread@example.com", now=start + step * (login_throttle.WINDOW_SECONDS / 4 + 1))
        self.assertEqual(login_throttle.seconds_locked("spread@example.com", now=start + 4 * (login_throttle.WINDOW_SECONDS / 4 + 1) + 1), 0)


if __name__ == "__main__":
    unittest.main()
