import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
import app.models
from app.main import app
from app.models.faq_item import FAQItem
from app.models.user import User
from app.security import create_access_token


class FAQAdminVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.headers = {"guest": {}}
        with Session(self.engine) as db:
            for role in ("admin", "free_user", "paid_user", "reporter"):
                user = User(full_name="Synthetic " + role, email=role+"@example.com", password_hash="not-used", role=role, is_active=True, referral_code="FAQ"+role)
                db.add(user)
                db.flush()
                self.headers[role] = {"Authorization": "Bearer " + create_access_token(user_id=user.id)}
                if role == "admin": admin_id = user.id
            for published in (True, False):
                item = FAQItem(question="Synthetic published" if published else "Synthetic hidden", answer="Synthetic answer", category="Local testing", is_published=published, created_by=admin_id)
                db.add(item)
                db.flush()
                if not published: self.hidden_id = item.id
            db.commit()
        def sessions():
            with Session(self.engine, expire_on_commit=False) as db:
                yield db
        app.dependency_overrides[get_db] = sessions
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_admin_lists_saved_hidden_and_published_items_after_new_request(self):
        for _ in range(2):
            response = self.client.get("/faq/admin", headers=self.headers["admin"])
            self.assertEqual(response.status_code, 200)
            self.assertEqual([(row["question"], row["is_published"]) for row in response.json()], [("Synthetic published", True), ("Synthetic hidden", False)])

    def test_public_list_and_detail_never_expose_hidden_faqs(self):
        for headers in self.headers.values():
            response = self.client.get("/faq", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual([row["question"] for row in response.json()], ["Synthetic published"])
            self.assertEqual(self.client.get(f"/faq/{self.hidden_id}", headers=headers).status_code, 404)

    def test_admin_listing_and_publication_actions_require_admin(self):
        for role, headers in self.headers.items():
            if role == "admin": continue
            expected = 401 if role == "guest" else 403
            self.assertEqual(self.client.get("/faq/admin", headers=headers).status_code, expected)
            self.assertEqual(self.client.patch(f"/faq/{self.hidden_id}/publish", headers=headers).status_code, expected)

    def test_hidden_publish_hide_delete_workflow_keeps_boundaries(self):
        headers = self.headers["admin"]
        item = self.client.post("/faq", headers=headers, json={"question":"Synthetic draft", "answer":"Synthetic content", "category":"Local testing"})
        self.assertEqual(item.status_code, 201)
        item_id = item.json()["id"]
        self.assertFalse(item.json()["is_published"])
        self.assertEqual(self.client.get(f"/faq/{item_id}").status_code, 404)
        self.assertEqual(self.client.patch(f"/faq/{item_id}/publish", headers=headers).status_code, 200)
        self.assertEqual(self.client.get(f"/faq/{item_id}").status_code, 200)
        self.assertEqual(self.client.patch(f"/faq/{item_id}/hide", headers=headers).status_code, 200)
        self.assertEqual(self.client.get(f"/faq/{item_id}").status_code, 404)
        self.assertIn(item_id, [row["id"] for row in self.client.get("/faq/admin", headers=headers).json()])
        self.assertEqual(self.client.delete(f"/faq/{item_id}", headers=headers).status_code, 204)
        self.assertNotIn(item_id, [row["id"] for row in self.client.get("/faq/admin", headers=headers).json()])
