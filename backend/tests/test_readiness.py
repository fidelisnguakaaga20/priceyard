"""Liveness stays cheap; readiness checks schema and redacts connection errors."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from app.main import app

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
        self.client = TestClient(app, raise_server_exceptions=False)
    def tearDown(self):
        self.client.close(); self.engine.dispose()
    def test_liveness_never_connects_to_database(self):
        with patch("app.database.get_engine", side_effect=RuntimeError("Synthetic private connection failure")) as database:
            self.assertEqual(self.client.get("/health").status_code, 200)
            database.assert_not_called()
            response = self.client.get("/ready")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"detail": "Service is not ready"})
    def test_only_current_schema_is_ready(self):
        with patch("app.database.get_engine", return_value=self.engine):
            self.assertEqual(self.client.get("/ready").status_code, 503)
            with self.engine.begin() as connection:
                connection.execute(text("CREATE TABLE alembic_version (version_num varchar(100))"))
                connection.execute(text("INSERT INTO alembic_version VALUES ('0021_feedback_screenshot')"))
            self.assertEqual(self.client.get("/ready").status_code, 503)
            with self.engine.begin() as connection:
                connection.execute(text("UPDATE alembic_version SET version_num='0025_notification_outbox'"))
            self.assertEqual(self.client.get("/ready").json(), {"status": "ready"})
