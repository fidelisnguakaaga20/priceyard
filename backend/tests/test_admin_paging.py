from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch

import anyio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment_schema import PaymentResponse
from app.schemas.user_schema import UserResponse
from app.security import create_access_token
from app.services.admin_list_service import AdminJSONResponse, admin_record_page, stream_admin_records

RESOURCES = ((User, UserResponse, (("id", False),), "/users"),
             (Payment, PaymentResponse, (("created_at", True), ("id", True)), "/payments"))


def seed_pages(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        moment = datetime(2026, 10, 18, 8, tzinfo=timezone.utc)
        users = [User(full_name=f"Synthetic page {index:03}", email=f"page-{index:03}@example.com",
                      password_hash="PRIVATE-PAGE-HASH", role="admin" if index == 0 else "free_user",
                      referral_code=f"PAGE{index:03}", created_at=moment) for index in range(205)]
        db.add_all(users); db.flush()
        for index, user in enumerate(users):
            db.add(Payment(user_id=user.id, reference=f"py_synthetic_page_{index:03}", plan="monthly", amount=2500,
                           currency="NGN", status=("pending", "success", "failed")[index % 3],
                           paystack_transaction_id=f"PRIVATE-PROVIDER-{index}", created_at=moment))
        db.commit()
        return users[0].id, users[1].id


def verify_pages(check, engine):
    seed_pages(engine)
    with Session(engine) as db:
        before = {model: db.execute(select(model.__table__).order_by(model.id)).all() for model, *_ in RESOURCES}
    max_hydrated = 0
    def loaded(db, item):
        nonlocal max_hydrated
        if db.get_bind() is engine:
            max_hydrated = max(max_hydrated, len(db.identity_map))
    event.listen(Session, "loaded_as_persistent", loaded)
    try:
        for model, schema, order, _ in RESOURCES:
            expected = sorted([row.id for row in before[model]], reverse=model is Payment)
            actual = []
            for offset, count in ((0, 100), (100, 100), (200, 5), (300, 0)):
                statements = []
                def query(*args):
                    statements.append(True)
                event.listen(engine, "before_cursor_execute", query)
                try:
                    with Session(engine) as db:
                        page = admin_record_page(db, model, schema, offset=offset, order=order)
                        check.assertLessEqual(len(db.identity_map), 100)
                finally:
                    event.remove(engine, "before_cursor_execute", query)
                check.assertEqual(len(statements), 1)
                check.assertEqual((page.total, page.offset, page.limit, len(page.items)), (205, offset, 100, count))
                check.assertEqual([row.id for row in page.items], expected[offset:offset+100])
                actual.extend(row.id for row in page.items)
            check.assertEqual(actual, expected)
            legacy = json.loads("".join(stream_admin_records(engine, model, schema, order=order)))
            check.assertEqual([row["id"] for row in legacy], expected)
            check.assertNotIn("PRIVATE", json.dumps(legacy))
            check.assertLessEqual(max_hydrated, 200)
        with Session(engine) as db:
            for model, *_ in RESOURCES:
                check.assertEqual(db.execute(select(model.__table__).order_by(model.id)).all(), before[model])
    finally:
        event.remove(Session, "loaded_as_persistent", loaded)


class AdminPagingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_complete_pages_counts_ties_stream_bounds_and_saved_rows(self):
        verify_pages(self, self.engine)

    def client(self):
        admin, customer = seed_pages(self.engine)
        def sessions():
            with Session(self.engine) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        return TestClient(app), {"Authorization": "Bearer " + create_access_token(user_id=admin)}, {"Authorization": "Bearer " + create_access_token(user_id=customer)}

    def test_original_complete_api_and_new_pages_keep_permissions_and_fields(self):
        client, admin, customer = self.client()
        with client:
            for _, _, _, path in RESOURCES:
                for endpoint in (path, path + "/page"):
                    self.assertEqual(client.get(endpoint).status_code, 401)
                    self.assertEqual(client.get(endpoint, headers=customer).status_code, 403)
                legacy = client.get(path, headers=admin)
                self.assertEqual(legacy.status_code, 200)
                self.assertEqual(len(legacy.json()), 205)
                self.assertNotIn("content-length", legacy.headers)
                collected = []
                for offset in (0, 100, 200):
                    response = client.get(f"{path}/page?offset={offset}", headers=admin)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()["total"], 205)
                    collected.extend(response.json()["items"])
                self.assertEqual(collected, legacy.json())
                self.assertNotIn("PRIVATE", legacy.text)
                for value in ("-1", "2147483648", "bad"):
                    self.assertEqual(client.get(f"{path}/page?offset={value}", headers=admin).status_code, 422)

    def test_empty_page_returns_complete_zero_total_without_hydrating_records(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            for model, schema, order, _ in RESOURCES:
                page = admin_record_page(db, model, schema, offset=100, order=order)
                self.assertEqual(page.model_dump(), {"items": [], "total": 0, "offset": 100, "limit": 100})
                self.assertEqual(json.loads("".join(stream_admin_records(self.engine, model, schema, order=order))), [])

    def test_failed_send_closes_the_legacy_stream(self):
        closed = []
        def content():
            try:
                yield "["
                yield "]"
            finally:
                closed.append(True)
        async def send(message):
            if message["type"] == "http.response.body":
                raise OSError("Synthetic disconnect")
        async def receive():
            return {"type": "http.disconnect"}
        async def run():
            with self.assertRaises(Exception):
                await AdminJSONResponse(content())({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
        anyio.run(run)
        self.assertEqual(closed, [True])

    def test_query_failure_closes_the_owned_stream_session(self):
        with patch("app.services.admin_list_service.Session") as sessions:
            sessions.return_value.__enter__.return_value.scalars.side_effect = RuntimeError("Synthetic query failure")
            with self.assertRaises(RuntimeError):
                next(stream_admin_records(self.engine, User, UserResponse, order=(("id", False),)))
            sessions.return_value.__exit__.assert_called_once()

    def test_cancelled_response_closes_its_source(self):
        closed = []
        def content():
            try:
                yield "["
                yield "]"
            finally:
                closed.append(True)
        async def run():
            started = anyio.Event()
            async def send(message):
                if message["type"] == "http.response.body":
                    started.set()
                    await anyio.sleep_forever()
            async def receive():
                return {"type": "http.disconnect"}
            async with anyio.create_task_group() as group:
                group.start_soon(AdminJSONResponse(content()), {"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
                await started.wait()
                group.cancel_scope.cancel()
        anyio.run(run)
        self.assertEqual(closed, [True])
