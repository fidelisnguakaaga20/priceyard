"""The developer API map (/docs, /redoc, /openapi.json) must not be public on the live server."""

import unittest

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


class ApiDocsHiddenTests(unittest.TestCase):
    def test_docs_are_off_by_default(self):
        self.assertFalse(get_settings().api_docs_enabled)

    def test_docs_pages_are_not_served(self):
        with TestClient(app) as client:
            for path in ("/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"):
                with self.subTest(path=path):
                    self.assertEqual(client.get(path).status_code, 404)
            self.assertEqual(client.get("/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
