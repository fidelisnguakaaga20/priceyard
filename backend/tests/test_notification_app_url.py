from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Base
import app.models
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist
from app.services.watchlist_alert_service import _notification_prices_url, notify_watchlist_subscribers


def configured(url, environment='staging'):
    return SimpleNamespace(frontend_url=url, app_env=environment)


class NotificationURLPolicy(unittest.TestCase):
    def test_https_staging_and_optional_trailing_slash(self):
        for value in ('https://staging.example.invalid', 'https://staging.example.invalid/'):
            self.assertEqual(_notification_prices_url(configured(value)), 'https://staging.example.invalid/prices')

    def test_production_keeps_original_destination_when_configured(self):
        self.assertEqual(_notification_prices_url(configured('https://priceyard.onrender.com/', 'production')),
                         'https://priceyard.onrender.com/prices')

    def test_missing_settings_default_is_not_an_explicit_destination(self):
        # No dotenv or application environment is consulted by these instances.
        with patch.dict('os.environ', {'APP_ENV': 'staging'}, clear=True):
            omitted = Settings(_env_file=None)
        self.assertNotIn('frontend_url', omitted.model_fields_set)
        with self.assertRaises(ValueError):
            _notification_prices_url(omitted)

    def test_nonproduction_cannot_use_known_live_host(self):
        for environment in ('staging', 'test', 'development'):
            for host in ('priceyard.onrender.com', 'PRICEYARD.onrender.com', 'sub.priceyard.onrender.com'):
                with self.subTest(environment=environment, host=host), self.assertRaises(ValueError):
                    _notification_prices_url(configured('https://'+host, environment))

    def test_malformed_or_unsafe_origins_fail_without_echoing_input(self):
        for value in (None, '', ' ', 'https://', '//staging.example.invalid', 'javascript:alert(1)',
                      'http://staging.example.invalid', 'https://staging.example.invalid/path',
                      'https://staging.example.invalid?next=https://priceyard.onrender.com',
                      'https://staging.example.invalid/#', 'https://staging.example.invalid?',
                      'https://user:synthetic-secret@staging.example.invalid',
                      'https://staging.example.invalid:bad', 'https://staging.example.invalid:99999',
                      'https://staging.example.invalid:0', 'https://bad_host.example.invalid',
                      'https://staging.example.invalid.', 'https://staging.example.invalid\\@priceyard.onrender.com',
                      'https://staging.example.invalid/%2f%2fpriceyard.onrender.com',
                      'https://staging.example.invalid\r\nBcc: synthetic@example.com',
                      'https://staging.example.invalid\t', 'https://127.0.0.1', 'https://10.0.0.1',
                      'http://127.0.0.1:55446', 'https://[::1]', 'https://localhost'):
            with self.subTest(value=value), self.assertRaises(ValueError) as error:
                _notification_prices_url(configured(value))
            self.assertEqual(str(error.exception), 'Notification application URL is not configured safely')

    def test_loopback_http_only_in_explicit_local_environments(self):
        for environment in ('development', 'test'):
            self.assertEqual(_notification_prices_url(configured('http://127.0.0.1:55446', environment)),
                             'http://127.0.0.1:55446/prices')
        for environment in ('production', 'staging', None, 'unknown'):
            with self.subTest(environment=environment), self.assertRaises(ValueError):
                _notification_prices_url(configured('http://127.0.0.1:55446', environment))

    def test_invalid_configuration_sends_nothing_and_never_queries_watchers(self):
        for value in (None, '', 'https://priceyard.onrender.com', 'http://staging.example.invalid'):
            db = Mock()
            with patch('app.config.get_settings', return_value=configured(value)), \
                    patch('app.services.email_service.send_email') as mail, \
                    patch('app.services.push_service.send_push_to_user') as push, \
                    patch('app.services.whatsapp_service.send_whatsapp_message') as whatsapp:
                self.assertEqual(notify_watchlist_subscribers(db, Mock()), 0)
                mail.assert_not_called(); push.assert_not_called(); whatsapp.assert_not_called()
                self.assertEqual(db.mock_calls, [])


class NotificationURLDelivery(unittest.TestCase):
    def test_production_email_keeps_original_link_and_count(self):
        user = SimpleNamespace(id=1, full_name='Synthetic watcher', email='watcher@example.com', is_active=True, phone=None)
        price = SimpleNamespace(commodity_id=1, market_id=1, commodity=SimpleNamespace(name='Egusi'),
                                market=SimpleNamespace(name='Kwali Market'), price_low=210000, price_high=220000, unit='1 bag')
        db = Mock()
        db.scalars.return_value.all.return_value = [SimpleNamespace(user=user, target_price=None)]
        with patch('app.config.get_settings', return_value=configured('https://priceyard.onrender.com/', 'production')), \
                patch('app.services.email_service.send_email') as mail, \
                patch('app.services.push_service.send_push_to_user', return_value=1):
            self.assertEqual(notify_watchlist_subscribers(db, price), 1)
            self.assertIn('Check it here: https://priceyard.onrender.com/prices\n\n', mail.call_args.kwargs['body'])
            self.assertEqual(mail.call_args.kwargs['recipient'], 'watcher@example.com')

    def test_all_staging_message_links_use_only_the_configured_application(self):
        engine = create_engine('sqlite+pysqlite:///:memory:')
        Base.metadata.create_all(engine)
        try:
            with Session(engine) as db:
                user = User(full_name='Synthetic watcher', email='watcher@example.com', phone='+2348000000001',
                            password_hash='synthetic-unused', role='admin', referral_code='URLTEST')
                commodity = Commodity(name='Egusi'); market = Market(name='Kwali Market')
                db.add_all([user, commodity, market]); db.flush()
                price = PriceUpdate(commodity_id=commodity.id, market_id=market.id, price_low=210000,
                                    price_high=220000, unit='1 bag', movement='unknown',
                                    confidence_level='Low confidence', update_date_time=datetime.now(timezone.utc),
                                    status='approved', created_by=user.id)
                db.add_all([price, Watchlist(user_id=user.id, commodity_id=commodity.id)]); db.commit()
                with patch('app.config.get_settings', return_value=configured('https://staging.example.invalid/')), \
                        patch('app.services.email_service.send_email') as mail, \
                        patch('app.services.push_service.send_push_to_user', return_value=1) as push, \
                        patch('app.services.whatsapp_service.send_whatsapp_message') as whatsapp:
                    self.assertEqual(notify_watchlist_subscribers(db, price), 1)
                    self.assertIn('Check it here: https://staging.example.invalid/prices', mail.call_args.kwargs['body'])
                    self.assertEqual(push.call_args.kwargs['url'], 'https://staging.example.invalid/prices')
                    self.assertIn('https://staging.example.invalid/prices', whatsapp.call_args.kwargs['body'])
                    for body in (mail.call_args.kwargs['body'], push.call_args.kwargs['url'], whatsapp.call_args.kwargs['body']):
                        self.assertNotIn('priceyard.onrender.com', body)
                    self.assertEqual(price.status, 'approved')
        finally:
            engine.dispose()
