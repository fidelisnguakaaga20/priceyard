"""Historical evidence stays intact while private audit fields stay off the wire."""
from copy import deepcopy
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.audit_log import AuditLog
from app.models.user import User
from app.security import create_access_token


LEGACY_VALUE = {
    "price_low": "210000.00", "notes": "Synthetic retained observation",
    "source_1": "SYNTHETIC-PRIVATE-SOURCE", "SOURCE_2": "SYNTHETIC-OTHER-SOURCE",
    "password_hash": "SYNTHETIC-PASSWORD-HASH", "screenshot_data": "SYNTHETIC-PRIVATE-ATTACHMENT",
    "nested": [{"Authorization": "SYNTHETIC-AUTHORIZATION", "refresh_token": "SYNTHETIC-TOKEN",
                "source_1": "SYNTHETIC-NESTED-SOURCE", "SENSE": "Retained"}],
}
SAFE_VALUE = {
    "price_low": "210000.00", "notes": "Synthetic retained observation",
    "nested": [{"SENSE": "Retained"}],
}


class AuditResponsePrivacyTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.headers = {}
        with Session(self.engine) as db:
            for role in ("admin", "reporter", "paid_user", "free_user"):
                user = User(full_name="Synthetic privacy user", email=role + "@example.com",
                            password_hash="unused", role=role, referral_code="AUDIT" + role.upper())
                db.add(user)
                db.flush()
                self.headers[role] = {"Authorization": "Bearer " + create_access_token(user_id=user.id)}
                if role == "admin":
                    self.admin_id = user.id
            item = AuditLog(user_id=self.admin_id, action="synthetic.legacy", table_name="price_updates",
                            record_id=1, old_value=deepcopy(LEGACY_VALUE), new_value=[deepcopy(LEGACY_VALUE), None])
            db.add(item)
            db.commit()
            self.item_id = item.id

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_admin_list_and_detail_redact_nested_legacy_fields_without_rewriting_evidence(self):
        with Session(self.engine) as db:
            before = db.execute(select(AuditLog.__table__)).all()
        for endpoint in ("/audit-logs", f"/audit-logs/{self.item_id}"):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint, headers=self.headers["admin"])
                self.assertEqual(response.status_code, 200)
                value = response.json()[0] if endpoint == "/audit-logs" else response.json()
                self.assertEqual(value["old_value"], SAFE_VALUE)
                self.assertEqual(value["new_value"], [SAFE_VALUE, None])
                self.assertEqual(value["action"], "synthetic.legacy")
                self.assertEqual(value["user_id"], self.admin_id)
        with Session(self.engine) as db:
            self.assertEqual(db.execute(select(AuditLog.__table__)).all(), before)

    def test_guest_and_other_roles_cannot_read_either_audit_endpoint(self):
        for endpoint in ("/audit-logs", f"/audit-logs/{self.item_id}"):
            self.assertEqual(self.client.get(endpoint).status_code, 401)
            for role in ("reporter", "paid_user", "free_user"):
                with self.subTest(endpoint=endpoint, role=role):
                    self.assertEqual(self.client.get(endpoint, headers=self.headers[role]).status_code, 403)

    def test_serializer_keeps_null_empty_values_and_input_objects_unchanged(self):
        from app.schemas.audit_log_schema import AuditLogResponse
        from datetime import datetime, timezone
        original = deepcopy(LEGACY_VALUE)
        for old, new, expected_old, expected_new in ((None, {}, None, {}), ([], None, [], None),
                                                    (original, [original], SAFE_VALUE, [SAFE_VALUE])):
            value = AuditLogResponse(id=1, user_id=self.admin_id, action="synthetic.legacy", table_name="price_updates",
                                     record_id=1, old_value=old, new_value=new, created_at=datetime.now(timezone.utc))
            serialized = value.model_dump(mode="json")
            self.assertEqual(serialized["old_value"], expected_old)
            self.assertEqual(serialized["new_value"], expected_new)
        self.assertEqual(original, LEGACY_VALUE)
