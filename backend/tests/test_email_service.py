import json
import unittest
from unittest.mock import patch

from app.config import Settings
from app.services.email_service import send_password_reset_email


class _Response:
    status = 201

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class BrevoEmailTests(unittest.TestCase):
    @patch("app.services.email_service.urlopen", return_value=_Response())
    @patch("app.services.email_service.get_settings")
    def test_brevo_sends_reset_email_without_exposing_key(self, mock_settings, mock_urlopen) -> None:
        mock_settings.return_value = Settings(
            brevo_api_key="secret-api-key",
            smtp_from_email="verified@example.com",
            smtp_from_name="PriceYard",
        )

        send_password_reset_email(
            recipient="user@example.com",
            reset_url="https://priceyard.onrender.com/reset-password?token=raw-token",
        )

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.get_header("Api-key"), "secret-api-key")
        self.assertEqual(payload["to"], [{"email": "user@example.com"}])
        self.assertIn("raw-token", payload["textContent"])
        self.assertNotIn("secret-api-key", request.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
