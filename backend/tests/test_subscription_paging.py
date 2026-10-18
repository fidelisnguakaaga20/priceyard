from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription_schema import SubscriptionResponse
from app.security import create_access_token
from app.services import subscription_service as service
from app.services.admin_list_service import admin_record_page, stream_admin_records

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def seed_subscriptions(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        for index in range(205):
            role = "admin" if index == 0 else "reporter" if index % 7 == 0 else "paid_user"
            user = User(full_name="Synthetic subscriber", email=f"paging-sub-{index}@example.com",
                        password_hash="unused", role=role, referral_code=f"SP{index}")
            kind = index % 5
            user.subscription = Subscription(status="trial" if kind == 0 else "active", plan_name="trial" if kind == 0 else "paid_monthly",
                trial_started_at=NOW-timedelta(days=15) if kind == 0 else None,
                trial_ends_at=NOW-timedelta(minutes=1) if kind == 0 else None,
                start_date=NOW.date()-timedelta(days=31) if kind else None,
                end_date=NOW.date()-timedelta(days=1) if kind == 1 else NOW.date() if kind == 2 else
                    NOW.date()+timedelta(days=30) if kind == 3 else None,
                payment_reference=f"synthetic_preserved_{index}")
            db.add(user)
        db.commit()
        before = db.execute(select(Subscription.__table__).order_by(Subscription.id)).all()
        users = {row.id: row for row in db.execute(select(User.__table__)).all()}
        return before, users


def verify_subscription_pages(check, engine):
    before, users = seed_subscriptions(engine)
    sizes = []
    with Session(engine) as db, patch.object(service, "utc_now", return_value=NOW):
        def memory(session, instance): sizes.append(len(session.identity_map))
        event.listen(db, "loaded_as_persistent", memory)
        service.expire_subscriptions_for_listing(db)
        check.assertLess(max(sizes), 10)
    with Session(engine) as db:
        after = db.execute(select(Subscription.__table__).order_by(Subscription.id)).all()
        after_users = {row.id: row for row in db.execute(select(User.__table__)).all()}
    for old, new in zip(before, after):
        due = old.status == "trial" or (old.end_date is not None and old.end_date < NOW.date())
        check.assertEqual(new.status, "expired" if due else old.status)
        check.assertEqual({k: v for k, v in old._mapping.items() if k not in {'status', 'updated_at'}},
                          {k: v for k, v in new._mapping.items() if k not in {'status', 'updated_at'}})
        role = users[old.user_id].role
        check.assertEqual(after_users[old.user_id].role, 'free_user' if due and role not in {'admin', 'reporter'} else role)
    ids = []
    for offset, count in ((0, 100), (100, 100), (200, 5), (300, 0)):
        with Session(engine) as db:
            page = admin_record_page(db, Subscription, SubscriptionResponse, offset=offset, order=(("id", False),))
            check.assertEqual((page.total, len(page.items)), (205, count))
            check.assertLessEqual(len(db.identity_map), 100)
            ids.extend(row.id for row in page.items)
    check.assertEqual(ids, [row.id for row in before])
    check.assertEqual(ids, [row['id'] for row in json.loads(''.join(stream_admin_records(
        engine, Subscription, SubscriptionResponse, order=(("id", False),))))])


class SubscriptionPagingTests(unittest.TestCase):
    def setUp(self): self.engine = create_engine('sqlite+pysqlite:///:memory:')
    def tearDown(self): app.dependency_overrides.clear(); self.engine.dispose()

    def test_all_account_expiry_bounded_hydration_pages_and_preserved_value(self):
        verify_subscription_pages(self, self.engine)

    def test_page_and_complete_legacy_array_keep_admin_only_access(self):
        before, users = seed_subscriptions(self.engine)
        def sessions():
            with Session(self.engine) as db: yield db
        app.dependency_overrides[get_db] = sessions
        admin = {'Authorization': 'Bearer ' + create_access_token(user_id=before[0].user_id)}
        other = {'Authorization': 'Bearer ' + create_access_token(user_id=before[1].user_id)}
        with TestClient(app) as client, patch.object(service, 'utc_now', return_value=NOW):
            for path in ('/subscriptions', '/subscriptions/admin/page'):
                self.assertEqual(client.get(path).status_code, 401)
                self.assertEqual(client.get(path, headers=other).status_code, 403)
            page = client.get('/subscriptions/admin/page?offset=200', headers=admin).json()
            self.assertEqual((page['total'], len(page['items'])), (205, 5))
            self.assertEqual(len(client.get('/subscriptions', headers=admin).json()), 205)
            self.assertEqual(client.get('/subscriptions/admin/page?offset=-1', headers=admin).status_code, 422)

    def test_failed_sweep_rolls_back_all_expiries_and_staff_roles(self):
        before, users = seed_subscriptions(self.engine)
        original = service.lock_subscription_state
        calls = 0
        def fail_second(db, user_id):
            nonlocal calls
            calls += 1
            if calls == 2: raise RuntimeError('Synthetic expiry failure')
            return original(db, user_id)
        with Session(self.engine) as db, patch.object(service, 'utc_now', return_value=NOW), patch.object(service, 'lock_subscription_state', side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, 'Synthetic expiry failure'):
                service.expire_subscriptions_for_listing(db)
        with Session(self.engine) as db:
            self.assertEqual(db.execute(select(Subscription.__table__).order_by(Subscription.id)).all(), before)
            self.assertEqual({row.id: row for row in db.execute(select(User.__table__)).all()}, users)
