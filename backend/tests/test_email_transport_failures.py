import json
import ssl
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from app.services import email_service


def settings(**overrides):
    value = dict(smtp_from_email='sender@example.com', smtp_from_name='PriceYard',
                 brevo_api_key='synthetic-only-not-a-real-key', brevo_api_url='https://mail.example.invalid/send',
                 smtp_host=None, smtp_port=587, smtp_username='synthetic-user', smtp_password='synthetic-password',
                 smtp_use_tls=True, smtp_use_ssl=False)
    value.update(overrides)
    return SimpleNamespace(**value)


class EmailTransportFailures(unittest.TestCase):
    def send(self):
        email_service.send_email(recipient='receiver@example.com', subject='Synthetic test', body='Synthetic only')

    def test_unconfigured_sender_or_transport_never_attempts_delivery(self):
        for config in (settings(smtp_from_email=None), settings(brevo_api_key=None, smtp_host=None)):
            with self.subTest(configured_sender=bool(config.smtp_from_email)), \
                    patch.object(email_service, 'get_settings', return_value=config), \
                    patch.object(email_service, 'urlopen') as http, patch.object(email_service.smtplib, 'SMTP') as smtp:
                with self.assertRaisesRegex(RuntimeError, 'not configured'): self.send()
                http.assert_not_called(); smtp.assert_not_called()

    def test_brevo_rejects_nonaccepted_status_without_success_or_smtp_fallback(self):
        for status in (400, 401, 429, 500):
            response = MagicMock(); response.__enter__.return_value.status = status
            with self.subTest(status=status), patch.object(email_service, 'get_settings', return_value=settings()), \
                    patch.object(email_service, 'urlopen', return_value=response) as http, \
                    patch.object(email_service.smtplib, 'SMTP') as smtp:
                with self.assertRaisesRegex(RuntimeError, str(status)): self.send()
                self.assertEqual(http.call_args.kwargs['timeout'], 15); smtp.assert_not_called()

    def test_brevo_http_and_connection_errors_do_not_expose_provider_details(self):
        errors = (HTTPError('https://mail.example.invalid/send', 401, 'synthetic-private-body', {}, None),
                  URLError('synthetic-password provider detail'))
        for error in errors:
            with patch.object(email_service, 'get_settings', return_value=settings()), \
                    patch.object(email_service, 'urlopen', side_effect=error):
                with self.assertRaises(RuntimeError) as caught: self.send()
                self.assertNotIn('synthetic-password', str(caught.exception))
                self.assertNotIn('synthetic-private-body', str(caught.exception))

    def test_smtp_starttls_precedes_login_and_send_with_verified_context(self):
        events = []
        server = MagicMock()
        server.ehlo.side_effect = lambda: events.append('ehlo')
        def starttls(*, context):
            self.assertTrue(context.check_hostname); self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            events.append('tls')
        server.starttls.side_effect = starttls
        server.login.side_effect = lambda *args: events.append('login')
        server.send_message.side_effect = lambda message: events.append('send')
        transport = MagicMock(); transport.__enter__.return_value = server
        with patch.object(email_service, 'get_settings', return_value=settings(brevo_api_key=None, smtp_host='smtp.example.invalid')), \
                patch.object(email_service.smtplib, 'SMTP', return_value=transport) as smtp:
            self.send(); self.assertEqual(smtp.call_args.kwargs['timeout'], 15)
        self.assertEqual(events, ['ehlo', 'tls', 'ehlo', 'login', 'send'])

    def test_smtp_tls_failure_cannot_send_login_or_message(self):
        server = MagicMock(); server.starttls.side_effect = ssl.SSLError('synthetic TLS failure')
        transport = MagicMock(); transport.__enter__.return_value = server
        with patch.object(email_service, 'get_settings', return_value=settings(brevo_api_key=None, smtp_host='smtp.example.invalid')), \
                patch.object(email_service.smtplib, 'SMTP', return_value=transport):
            with self.assertRaises(ssl.SSLError): self.send()
        server.login.assert_not_called(); server.send_message.assert_not_called()

    def test_smtp_ssl_uses_verified_context_and_never_plain_smtp(self):
        transport = MagicMock()
        with patch.object(email_service, 'get_settings', return_value=settings(brevo_api_key=None, smtp_host='smtp.example.invalid', smtp_port=465, smtp_use_ssl=True)), \
                patch.object(email_service.smtplib, 'SMTP_SSL', return_value=transport) as tls, \
                patch.object(email_service.smtplib, 'SMTP') as plain:
            self.send()
            self.assertEqual(tls.call_args.kwargs['timeout'], 15)
            context = tls.call_args.kwargs['context']
            self.assertTrue(context.check_hostname); self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            plain.assert_not_called(); transport.__enter__.return_value.send_message.assert_called_once()
