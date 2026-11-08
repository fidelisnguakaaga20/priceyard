from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select

from app.database import get_session_factory
from app.main import app
from app.models.faq_item import FAQItem
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage14-Test-Password!"
admin_email = f"stage14-admin-{run_id}@example.com"
user_email = f"stage14-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_user_id: int | None = None
normal_user_id: int | None = None
faq_ids: list[int] = []

PRICE_DISCLAIMER = (
    "Prices are market estimates and may change based on quality, quantity, negotiation, "
    "transport cost, bag size, time of day, and market conditions. PriceYard provides "
    "market information only and does not guarantee profit or exact transaction prices."
)


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


def login(email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    check(f"login works for {email}", response.status_code == 200)
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


try:
    with SessionLocal() as db:
        inspector = inspect(db.get_bind())
        tables = set(inspector.get_table_names())
        check("Stage 3 faq_items table still exists", "faq_items" in tables)
        columns = {item["name"] for item in inspector.get_columns("faq_items")}
        check(
            "faq_items approved fields exist",
            {
                "id",
                "question",
                "answer",
                "category",
                "is_published",
                "created_by",
                "created_at",
                "updated_at",
            }.issubset(columns),
        )

        admin = User(
            full_name="Stage 14 Admin",
            email=admin_email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_user_id = admin.id

    registration = client.post(
        "/auth/register",
        json={"full_name": "Stage 14 User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    normal_user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)

    public_list = client.get("/faq")
    check("public FAQ list is accessible", public_list.status_code == 200)

    valid_payload = {
        "question": "Why does PriceYard use price ranges?",
        "answer": (
            "Market prices can vary with quality, quantity, negotiation, bag size, time of day, "
            "and market conditions, so a verified range can be more useful than false exact precision."
        ),
        "category": "prices",
    }

    check(
        "non-admin FAQ creation blocked",
        client.post("/faq", json=valid_payload, headers=auth(user_token)).status_code == 403,
    )
    check(
        "FAQ create cannot bypass publish flow",
        client.post(
            "/faq",
            json={**valid_payload, "is_published": True},
            headers=auth(admin_token),
        ).status_code == 422,
    )
    check(
        "guaranteed-profit FAQ content rejected",
        client.post(
            "/faq",
            json={
                "question": "Will this always make money?",
                "answer": "Profit is guaranteed when you follow this instruction.",
                "category": "disclaimer",
            },
            headers=auth(admin_token),
        ).status_code == 422,
    )
    check(
        "private account instruction rejected",
        client.post(
            "/faq",
            json={
                "question": "Where should I transfer money?",
                "answer": "Transfer to account number 1234567890 for access.",
                "category": "subscription",
            },
            headers=auth(admin_token),
        ).status_code == 422,
    )
    check(
        "private phone instruction rejected",
        client.post(
            "/faq",
            json={
                "question": "Who should I contact?",
                "answer": "Call 08012345678 for private instructions.",
                "category": "subscription",
            },
            headers=auth(admin_token),
        ).status_code == 422,
    )

    created = client.post("/faq", json=valid_payload, headers=auth(admin_token))
    check("admin FAQ create works", created.status_code == 201)
    created_body = created.json()
    faq_id = created_body["id"]
    faq_ids.append(faq_id)
    check("new FAQ starts hidden", created_body["is_published"] is False)
    check("FAQ creator is server-controlled admin", created_body["created_by"] == admin_user_id)
    check("FAQ content is preserved", created_body["answer"] == valid_payload["answer"])

    check("hidden FAQ is not publicly visible", client.get(f"/faq/{faq_id}").status_code == 404)
    hidden_list = client.get("/faq")
    check(
        "hidden FAQ is absent from public list",
        all(item["id"] != faq_id for item in hidden_list.json()),
    )

    edited_answer = (
        "Price ranges reduce false precision because prices may differ by quality, quantity, "
        "negotiation, bag size, time of day, and market conditions."
    )
    edit = client.patch(
        f"/faq/{faq_id}",
        json={"answer": edited_answer},
        headers=auth(admin_token),
    )
    check("admin FAQ edit works", edit.status_code == 200)
    check("FAQ edit persisted", edit.json()["answer"] == edited_answer)
    check(
        "non-admin FAQ edit blocked",
        client.patch(
            f"/faq/{faq_id}",
            json={"answer": "Unauthorized change."},
            headers=auth(user_token),
        ).status_code == 403,
    )

    check(
        "non-admin FAQ publish blocked",
        client.patch(f"/faq/{faq_id}/publish", headers=auth(user_token)).status_code == 403,
    )
    publish = client.patch(f"/faq/{faq_id}/publish", headers=auth(admin_token))
    check("admin FAQ publish works", publish.status_code == 200)
    check("FAQ published state persisted", publish.json()["is_published"] is True)

    public_item = client.get(f"/faq/{faq_id}")
    check("published FAQ is publicly visible", public_item.status_code == 200)
    check("public FAQ preserves edited content", public_item.json()["answer"] == edited_answer)
    check("public FAQ does not expose creator id", "created_by" not in public_item.json())
    check("public FAQ does not expose publication control", "is_published" not in public_item.json())
    published_list = client.get("/faq")
    check("published FAQ appears in public list", any(item["id"] == faq_id for item in published_list.json()))

    disclaimer_payload = {
        "question": "Does PriceYard guarantee profit or an exact transaction price?",
        "answer": PRICE_DISCLAIMER,
        "category": "disclaimer",
    }
    disclaimer_create = client.post("/faq", json=disclaimer_payload, headers=auth(admin_token))
    check("approved disclaimer FAQ can be created", disclaimer_create.status_code == 201)
    disclaimer_id = disclaimer_create.json()["id"]
    faq_ids.append(disclaimer_id)
    disclaimer_publish = client.patch(f"/faq/{disclaimer_id}/publish", headers=auth(admin_token))
    check("approved disclaimer FAQ can be published", disclaimer_publish.status_code == 200)
    disclaimer_public = client.get(f"/faq/{disclaimer_id}")
    check("required price disclaimer is preserved", disclaimer_public.json()["answer"] == PRICE_DISCLAIMER)

    check(
        "non-admin FAQ hide blocked",
        client.patch(f"/faq/{faq_id}/hide", headers=auth(user_token)).status_code == 403,
    )
    hide = client.patch(f"/faq/{faq_id}/hide", headers=auth(admin_token))
    check("admin FAQ hide works", hide.status_code == 200)
    check("FAQ hidden state persisted", hide.json()["is_published"] is False)
    check("hidden FAQ stops being publicly visible", client.get(f"/faq/{faq_id}").status_code == 404)
    after_hide = client.get("/faq")
    check("hidden FAQ disappears from public list", all(item["id"] != faq_id for item in after_hide.json()))

    check(
        "non-admin FAQ delete blocked",
        client.delete(f"/faq/{faq_id}", headers=auth(user_token)).status_code == 403,
    )
    deleted = client.delete(f"/faq/{faq_id}", headers=auth(admin_token))
    check("admin FAQ delete works", deleted.status_code == 204)
    faq_ids.remove(faq_id)
    check("deleted FAQ no longer exists publicly", client.get(f"/faq/{faq_id}").status_code == 404)

    with SessionLocal() as db:
        persisted = db.get(FAQItem, disclaimer_id)
        check("SQLAlchemy FAQ relationship works", persisted is not None and persisted.creator.id == admin_user_id)

    print(checks)
    print("STAGE 14 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if faq_ids:
            for item in list(db.scalars(select(FAQItem).where(FAQItem.id.in_(faq_ids))).all()):
                db.delete(item)
            db.commit()

        if normal_user_id is not None:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == normal_user_id))
            if subscription is not None:
                db.delete(subscription)
            user = db.get(User, normal_user_id)
            if user is not None:
                db.delete(user)

        if admin_user_id is not None:
            admin = db.get(User, admin_user_id)
            if admin is not None:
                db.delete(admin)
        db.commit()
