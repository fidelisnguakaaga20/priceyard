"""Attempt limits must count the real visitor (Cloudflare's CF-Connecting-IP), not a faked
X-Forwarded-For note that a visitor can change on every request."""

import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import Base, get_db
import app.models  # noqa: F401  (registers every table)
from app.main import app
from app.rate_limit import client_address, limiter


def request_with(headers: dict[str, str], peer: str = "10.0.0.5") -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "method": "GET", "path": "/", "headers": raw, "client": (peer, 1234)})


class ClientAddressTests(unittest.TestCase):
    def test_uses_cloudflare_address_and_ignores_faked_forwarding_note(self):
        request = request_with({"CF-Connecting-IP": "102.91.105.168", "X-Forwarded-For": "1.2.3.4"}, peer="1.2.3.4")
        self.assertEqual(client_address(request), "102.91.105.168")

    def test_ipv6_cloudflare_address_is_normalised(self):
        self.assertEqual(client_address(request_with({"CF-Connecting-IP": "2001:DB8::0001"})), "2001:db8::1")

    def test_falls_back_to_connection_when_header_missing_or_invalid(self):
        self.assertEqual(client_address(request_with({}, peer="127.0.0.1")), "127.0.0.1")
        self.assertEqual(client_address(request_with({"CF-Connecting-IP": "not-an-ip"}, peer="127.0.0.1")), "127.0.0.1")


class ForgotPasswordLimitTests(unittest.TestCase):
    def setUp(self):
        limiter.reset()
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        def sessions():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        limiter.reset()

    def forgot(self, headers):
        return self.client.post("/auth/forgot-password", json={"email": "nobody@example.com"}, headers=headers)

    def test_changing_fake_forwarding_note_does_not_escape_the_limit(self):
        for index in range(5):
            response = self.forgot({"CF-Connecting-IP": "102.91.105.168", "X-Forwarded-For": f"9.9.9.{index}"})
            self.assertEqual(response.status_code, 200)
        blocked = self.forgot({"CF-Connecting-IP": "102.91.105.168", "X-Forwarded-For": "9.9.9.99"})
        self.assertEqual(blocked.status_code, 429)

    def test_different_real_visitors_have_separate_limits(self):
        for _ in range(5):
            self.forgot({"CF-Connecting-IP": "102.91.105.168"})
        self.assertEqual(self.forgot({"CF-Connecting-IP": "41.58.1.2"}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
