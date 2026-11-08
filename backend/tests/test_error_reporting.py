from types import SimpleNamespace
from unittest.mock import patch
import json
import unittest

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import sentry_sdk
from sentry_sdk.transport import Transport

from app.error_reporting import init_error_reporting, scrub_event


# Fake private details, kept far from the failing line: Sentry quotes nearby source lines.
SECRET_QUERY = "/boom?email=secret-user@example.com"
SECRET_BODY = {"email": "secret-user@example.com", "password": "SuperSecretPassword1"}
SECRET_HEADERS = {
    "Authorization": "Bearer secret-login-token",
    "Cookie": "priceyard_session=secret-cookie",
    "CF-Connecting-IP": "203.0.113.9",
    "X-PriceYard-CSRF": "secret-csrf",
}
SECRET_VALUES = (
    "SuperSecretPassword1",
    "secret-user@example.com",
    "other-user@example.com",
    "secret-login-token",
    "secret-cookie",
    "203.0.113.9",
    "secret-csrf",
)


class CapturingTransport(Transport):
    def __init__(self, options=None):
        super().__init__(options)
        self.events = []

    def capture_envelope(self, envelope):
        for item in envelope.items:
            if item.type == "event":
                self.events.append(item.payload.json)


def settings(dsn):
    return SimpleNamespace(sentry_dsn=dsn, app_env="test")


class ErrorReportingTests(unittest.TestCase):
    """Owner-approved audit item 10: error alerts that never carry private data."""

    def tearDown(self):
        sentry_sdk.init(
            dsn=None, release="test", default_integrations=False
        )  # switch reporting back off for the other tests

    def test_does_nothing_without_dsn(self):
        with patch("sentry_sdk.init") as init:
            self.assertFalse(init_error_reporting(settings(None)))
            self.assertFalse(init_error_reporting(settings("   ")))
        init.assert_not_called()

    def test_reports_server_error_without_private_data(self):
        transport = CapturingTransport()
        real_init = sentry_sdk.init

        def init_with_test_transport(**options):
            options["transport"] = transport
            return real_init(**options)

        with patch("sentry_sdk.init", side_effect=init_with_test_transport):
            self.assertTrue(init_error_reporting(settings("https://publickey@o0.ingest.sentry.invalid/1")))

        demo = FastAPI()

        @demo.post("/boom")
        async def boom(request: Request):
            await request.body()
            raise RuntimeError("synthetic failure for the alert test (user " + "other-user@example.com" + ")")

        client = TestClient(demo, raise_server_exceptions=False)
        response = client.post(SECRET_QUERY, json=SECRET_BODY, headers=SECRET_HEADERS)
        self.assertEqual(response.status_code, 500)
        sentry_sdk.flush()

        self.assertEqual(len(transport.events), 1)
        sent = json.dumps(transport.events[0])
        self.assertIn("synthetic failure for the alert test", sent)
        self.assertNotIn("breadcrumbs", transport.events[0])
        for private in SECRET_VALUES:
            self.assertNotIn(private, sent)

    def test_scrub_keeps_only_safe_parts(self):
        event = {
            "request": {
                "data": {"password": "x"},
                "cookies": {"a": "b"},
                "query_string": "q=1",
                "headers": {"Authorization": "Bearer t", "User-Agent": "Phone"},
            },
            "user": {"id": 7, "email": "a@b.c", "ip_address": "1.2.3.4"},
        }
        cleaned = scrub_event(event)
        self.assertEqual(cleaned["request"], {"headers": {"User-Agent": "Phone"}})
        self.assertEqual(cleaned["user"], {"id": 7})


if __name__ == "__main__":
    unittest.main()
