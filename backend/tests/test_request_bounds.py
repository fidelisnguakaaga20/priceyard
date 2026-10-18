import asyncio
import hashlib
import json
import tracemalloc
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.request_bounds import (MAX_REQUEST_BODY_BYTES, MAX_REQUEST_HEADER_BYTES,
                                MAX_REQUEST_TARGET_BYTES, RequestBoundsMiddleware)
from app.security import create_access_token


def verify_database_rejection(check, engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner = User(full_name="Synthetic request bounds", email="bounds@example.com", password_hash="unused", role="admin", referral_code="BODYBOUND")
        commodity, market = Commodity(name="Egusi"), Market(name="Kwali Market")
        db.add_all([owner, commodity, market]); db.flush()
        from datetime import datetime, timezone
        price = PriceUpdate(commodity_id=commodity.id, market_id=market.id, unit="1 bag", bag_size=None,
                            price_low=210000, price_high=220000, status="approved", movement="unknown",
                            confidence_level="Low confidence", created_by=owner.id, update_date_time=datetime.now(timezone.utc))
        db.add(price); db.commit(); owner_id, price_id = owner.id, price.id
        before = db.execute(select(PriceUpdate.__table__)).all()
    def sessions():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = sessions
    queries = []
    def observe(*args):
        queries.append(True)
    event.listen(engine, "before_cursor_execute", observe)
    try:
        with TestClient(app) as client, patch("app.routes.payment_routes.verify_webhook_signature") as provider:
            for path in ("/auth/register", f"/price-updates/{price_id}", "/payments/webhook", "/feedback"):
                response = client.request("PATCH" if "price-updates" in path else "POST", path,
                                          headers={"content-length": str(MAX_REQUEST_BODY_BYTES + 1)}, content=b"{}")
                check.assertEqual(response.status_code, 413)
                check.assertEqual(response.json(), {"detail": "Request body is too large"})
            provider.assert_not_called()
            check.assertEqual(queries, [])
            headers = {"Authorization": "Bearer " + create_access_token(user_id=owner_id)}
            check.assertEqual(client.get("/price-updates/admin/history", headers=headers).status_code, 200)
        with Session(engine) as db:
            check.assertEqual(db.execute(select(PriceUpdate.__table__)).all(), before)
    finally:
        event.remove(engine, "before_cursor_execute", observe)
        app.dependency_overrides.clear()


class RequestBoundaryDatabaseTests(unittest.TestCase):
    def test_oversized_writes_are_rejected_before_database_or_payment_work(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        try:
            verify_database_rejection(self, engine)
        finally:
            engine.dispose()


class RequestBoundsTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, messages, *, headers=(), raw_path=b"/health", query=b"", limit=16):
        sent, calls, reads = [], [], 0
        iterator = iter(messages)
        async def receive():
            nonlocal reads
            reads += 1
            return next(iterator, {"type": "http.disconnect"})
        async def send(message):
            sent.append(message)
        async def endpoint(scope, receive, send):
            calls.append(await receive())
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})
        scope = {"type": "http", "method": "POST", "path": "/health", "raw_path": raw_path,
                 "query_string": query, "headers": list(headers)}
        await RequestBoundsMiddleware(endpoint, max_body_bytes=limit)(scope, receive, send)
        return sent, calls, reads

    async def test_boundary_and_fragmentation_preserve_exact_signed_bytes(self):
        body = b'{"name":"\xc3\xa9"}\r\n'
        for sizes in ((body,), tuple(bytes([value]) for value in body)):
            messages = [{"type": "http.request", "body": chunk, "more_body": index < len(sizes)-1} for index, chunk in enumerate(sizes)]
            sent, calls, _ = await self.invoke(messages, headers=[(b"content-length", str(len(body)).encode())], limit=len(body))
            self.assertEqual(sent[0]["status"], 200)
            self.assertEqual(calls, [{"type": "http.request", "body": body, "more_body": False}])
            self.assertEqual(hashlib.sha256(calls[0]["body"]).digest(), hashlib.sha256(body).digest())

    async def test_chunked_and_underdeclared_oversize_never_enter_application(self):
        for headers in ((), ((b"content-length", b"2"),)):
            messages = [{"type": "http.request", "body": b"a"*8, "more_body": True},
                        {"type": "http.request", "body": b"b"*9, "more_body": True}]
            sent, calls, reads = await self.invoke(messages, headers=headers)
            self.assertEqual(sent[0]["status"], 413); self.assertEqual(calls, []); self.assertEqual(reads, 2)

    async def test_declared_oversize_is_rejected_without_reading_input(self):
        sent, calls, reads = await self.invoke((), headers=[(b"content-length", b"17")])
        self.assertEqual(sent[0]["status"], 413); self.assertEqual(calls, []); self.assertEqual(reads, 0)

    async def test_malformed_conflicting_and_mismatched_lengths_fail_closed(self):
        for headers in ([(b"content-length", b"-1")], [(b"content-length", b"+1")],
                        [(b"content-length", b"1"*20)], [(b"content-length", b"2"), (b"content-length", b"3")],
                        [(b"content-length", b"3")]):
            sent, calls, _ = await self.invoke([{"type": "http.request", "body": b"{}"}], headers=headers)
            self.assertEqual(sent[0]["status"], 400); self.assertEqual(calls, [])

    async def test_url_and_header_limits_are_bytes_and_never_echo_private_input(self):
        for kwargs, status in (({"raw_path": b"/"*MAX_REQUEST_TARGET_BYTES, "query": b"x"}, 414),
                               ({"headers": [(b"authorization", b"PRIVATE"*MAX_REQUEST_HEADER_BYTES)]}, 431)):
            sent, calls, reads = await self.invoke((), **kwargs)
            self.assertEqual(sent[0]["status"], status); self.assertEqual(calls, []); self.assertEqual(reads, 0)
            self.assertNotIn(b"PRIVATE", b"".join(message.get("body", b"") for message in sent))

    async def test_disconnect_and_non_http_scope_do_not_create_partial_writes(self):
        sent, calls, _ = await self.invoke([{"type": "http.request", "body": b"a", "more_body": True}, {"type": "http.disconnect"}])
        self.assertEqual(sent, []); self.assertEqual(calls, [])
        called = []
        async def lifecycle(scope, receive, send):
            called.append(scope["type"])
        await RequestBoundsMiddleware(lifecycle)({"type": "lifespan"}, None, None)
        self.assertEqual(called, ["lifespan"])

    async def test_fragmented_input_has_bounded_memory_without_a_chunk_list(self):
        size = 65536
        messages = ({"type": "http.request", "body": b"a", "more_body": index < size-1} for index in range(size))
        tracemalloc.start()
        try:
            sent, calls, _ = await self.invoke(messages, limit=size)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(sent[0]["status"], 200)
        self.assertEqual(len(calls[0]["body"]), size)
        self.assertLess(peak, 512*1024)

    async def test_exact_url_header_budgets_and_concurrent_requests_are_independent(self):
        for kwargs in ({"raw_path": b"/"*MAX_REQUEST_TARGET_BYTES},
                       {"headers": [(b"x", b"a"*(MAX_REQUEST_HEADER_BYTES-5))]}):
            sent, _, _ = await self.invoke([{"type": "http.request", "body": b""}], **kwargs)
            self.assertEqual(sent[0]["status"], 200)
        results = await asyncio.gather(self.invoke([{"type": "http.request", "body": b"one"}]),
                                       self.invoke([{"type": "http.request", "body": b"x"*17}]))
        self.assertEqual([result[0][0]["status"] for result in results], [200, 413])
        self.assertEqual(results[0][1][0]["body"], b"one")
