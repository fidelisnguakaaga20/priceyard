from datetime import datetime, timezone
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback_schema import FeedbackResponse
from app.security import create_access_token
from app.services.admin_list_service import admin_record_page, stream_admin_records

ORDER = (("created_at", True), ("id", True))


def verify_feedback_pages(check, engine):
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = User(full_name="Synthetic Admin", email="feedback-page-admin@example.com", role="admin",
                     password_hash="unused", referral_code="FPADMIN")
        free = User(full_name="Synthetic Free", email="feedback-page-free@example.com", role="free_user",
                    password_hash="unused", referral_code="FPFREE")
        db.add_all([admin, free]); db.flush(); owner, customer = admin.id, free.id
        moment = datetime.now(timezone.utc)
        for index in range(205):
            db.add(Feedback(user_id=free.id, rating=1 if index == 204 else 5,
                comment=f"Synthetic comment {index:03}", complaint_or_suggestion="Saved feedback text",
                missing_market_request="PRIVATE-FEEDBACK-MARKER", screenshot_data="PRIVATE-ATTACHMENT-MARKER",
                is_public_testimonial=index == 0, testimonial_display_name="Synthetic public display" if index == 0 else None,
                created_at=moment))
        db.commit(); before = db.execute(select(Feedback.__table__).order_by(Feedback.id)).all()
    for rating, count in ((None, 205), (5, 204), (1, 1), (2, 0)):
        where = (Feedback.rating == rating,) if rating is not None else ()
        expected = [row.id for row in reversed(before) if rating is None or row.rating == rating]
        ids = []
        for offset in (0, 100, 200, 300):
            statements = []
            def observe(*args): statements.append(True)
            event.listen(engine, "before_cursor_execute", observe)
            try:
                with Session(engine) as db:
                    page = admin_record_page(db, Feedback, FeedbackResponse, offset=offset, order=ORDER, where=where)
                    check.assertLessEqual(len(db.identity_map), 100)
            finally: event.remove(engine, "before_cursor_execute", observe)
            check.assertEqual(len(statements), 1)
            check.assertEqual((page.total, len(page.items)), (count, len(expected[offset:offset + 100])))
            check.assertTrue(all(row.screenshot_data == 'PRIVATE-ATTACHMENT-MARKER' for row in page.items))
            ids.extend(row.id for row in page.items)
        check.assertEqual(ids, expected)
        streamed = json.loads(''.join(stream_admin_records(engine, Feedback, FeedbackResponse, order=ORDER, where=where)))
        check.assertEqual([row['id'] for row in streamed], expected)
    overrides = app.dependency_overrides.copy()
    def sessions():
        with Session(engine) as db: yield db
    app.dependency_overrides[get_db] = sessions
    try:
        with TestClient(app) as client:
            headers = {'Authorization': 'Bearer ' + create_access_token(user_id=owner)}
            for suffix in ('', '/admin/page', '/summary'):
                check.assertEqual(client.get('/feedback' + suffix).status_code, 401)
                check.assertEqual(client.get('/feedback' + suffix, headers={'Authorization': 'Bearer ' + create_access_token(user_id=customer)}).status_code, 403)
            summary = client.get('/feedback/summary', headers=headers).json()
            check.assertEqual(summary['count'], 205); check.assertAlmostEqual(summary['average_rating'], (204 * 5 + 1) / 205)
            page = client.get('/feedback/admin/page?rating=5&offset=200', headers=headers).json()
            check.assertEqual((page['total'], len(page['items'])), (204, 4))
            check.assertEqual(len(client.get('/feedback?rating=5', headers=headers).json()), 204)
            check.assertEqual(client.get('/feedback/summary', headers=headers).json(), summary)
            for suffix in ('?rating=6', '?offset=-1', '?offset=2147483648'):
                check.assertEqual(client.get('/feedback/admin/page' + suffix, headers=headers).status_code, 422)
            public = client.get('/testimonials').json()
            check.assertEqual(len(public), 1)
            check.assertEqual(set(public[0]), {'id', 'rating', 'quote', 'display_name', 'created_at'})
            check.assertNotIn('PRIVATE-', json.dumps(public))
    finally:
        app.dependency_overrides.clear(); app.dependency_overrides.update(overrides)
    with Session(engine) as db:
        check.assertEqual(db.execute(select(Feedback.__table__).order_by(Feedback.id)).all(), before)


class FeedbackPagingTests(unittest.TestCase):
    def test_filtered_snapshot_pages_keep_global_summary_and_testimonial_privacy(self):
        engine = create_engine('sqlite+pysqlite:///:memory:')
        try: verify_feedback_pages(self, engine)
        finally: engine.dispose()
