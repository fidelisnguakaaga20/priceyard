from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select

from app.database import get_session_factory
from app.main import app
from app.models.feedback import Feedback
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.password import hash_password

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage15-Test-Password!"
admin_email = f"stage15-admin-{run_id}@example.com"
user_email = f"stage15-user-{run_id}@example.com"
checks: dict[str, str] = {}
admin_user_id: int | None = None
normal_user_id: int | None = None
feedback_ids: list[int] = []


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
        check("Stage 3 feedback table still exists", "feedback" in tables)
        columns = {item["name"] for item in inspector.get_columns("feedback")}
        check(
            "feedback approved Stage 15 fields exist",
            {
                "id",
                "user_id",
                "rating",
                "comment",
                "price_usefulness",
                "price_accuracy",
                "missing_market_request",
                "missing_commodity_request",
                "complaint_or_suggestion",
                "continue_using_feedback",
                "willingness_to_pay_feedback",
                "created_at",
                "updated_at",
            }.issubset(columns),
        )

        admin = User(
            full_name="Stage 15 Admin",
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
        json={"full_name": "Stage 15 User", "email": user_email, "password": password},
    )
    check("normal user registration works", registration.status_code == 201)
    normal_user_id = registration.json()["id"]

    admin_token = login(admin_email)
    user_token = login(user_email)

    check(
        "unauthenticated feedback submission blocked",
        client.post("/feedback", json={"rating": 5}).status_code == 401,
    )
    check(
        "rating 0 fails",
        client.post("/feedback", json={"rating": 0}, headers=auth(user_token)).status_code == 422,
    )
    check(
        "rating 6 fails",
        client.post("/feedback", json={"rating": 6}, headers=auth(user_token)).status_code == 422,
    )
    check(
        "client cannot control feedback user link",
        client.post(
            "/feedback",
            json={"rating": 5, "user_id": admin_user_id},
            headers=auth(user_token),
        ).status_code == 422,
    )

    rating_one_payload = {
        "rating": 1,
        "comment": "The update format is understandable, but I need fresher data.",
        "price_usefulness": "Useful structure but update freshness matters.",
        "price_accuracy": "Needs continued verification.",
        "missing_market_request": "None",
        "missing_commodity_request": "None",
        "complaint_or_suggestion": "Keep timestamps prominent.",
        "continue_using_feedback": True,
        "willingness_to_pay_feedback": False,
    }
    first = client.post("/feedback", json=rating_one_payload, headers=auth(user_token))
    check("rating 1 works", first.status_code == 201)
    first_body = first.json()
    first_id = first_body["id"]
    feedback_ids.append(first_id)
    check("feedback user link is server-controlled current user", first_body["user_id"] == normal_user_id)
    check("feedback comment preserved", first_body["comment"] == rating_one_payload["comment"])
    check("continue-using feedback preserved", first_body["continue_using_feedback"] is True)
    check("willingness-to-pay feedback preserved", first_body["willingness_to_pay_feedback"] is False)

    rating_five_payload = {
        "rating": 5,
        "comment": "The price range and history are very useful.",
        "price_usefulness": "Very useful",
        "price_accuracy": "Clear when confidence is shown",
        "missing_market_request": "",
        "missing_commodity_request": "",
        "complaint_or_suggestion": "Keep verification labels visible.",
        "continue_using_feedback": True,
        "willingness_to_pay_feedback": True,
    }
    second = client.post("/feedback", json=rating_five_payload, headers=auth(user_token))
    check("rating 5 works", second.status_code == 201)
    second_id = second.json()["id"]
    feedback_ids.append(second_id)

    check(
        "non-admin cannot browse all private feedback",
        client.get("/feedback", headers=auth(user_token)).status_code == 403,
    )
    check(
        "non-admin cannot view feedback summary",
        client.get("/feedback/summary", headers=auth(user_token)).status_code == 403,
    )
    check(
        "non-admin cannot fetch another private feedback record through admin API",
        client.get(f"/feedback/{first_id}", headers=auth(user_token)).status_code == 403,
    )

    admin_list = client.get("/feedback", headers=auth(admin_token))
    check("admin can view feedback", admin_list.status_code == 200)
    admin_ids = {item["id"] for item in admin_list.json()}
    check("admin feedback list contains submitted feedback", {first_id, second_id}.issubset(admin_ids))

    rating_filter = client.get("/feedback?rating=5", headers=auth(admin_token))
    check("admin can filter feedback by rating", rating_filter.status_code == 200)
    check(
        "rating filter returns only rating 5",
        all(item["rating"] == 5 for item in rating_filter.json()) and any(item["id"] == second_id for item in rating_filter.json()),
    )
    check(
        "invalid admin rating filter rejected",
        client.get("/feedback?rating=6", headers=auth(admin_token)).status_code == 422,
    )

    admin_item = client.get(f"/feedback/{first_id}", headers=auth(admin_token))
    check("admin can read complaint or suggestion", admin_item.status_code == 200)
    check(
        "admin feedback detail preserves complaint or suggestion",
        admin_item.json()["complaint_or_suggestion"] == rating_one_payload["complaint_or_suggestion"],
    )

    summary = client.get("/feedback/summary", headers=auth(admin_token))
    check("admin feedback summary works", summary.status_code == 200)
    with SessionLocal() as db:
        expected_count, expected_average = db.execute(
            select(func.count(Feedback.id), func.avg(Feedback.rating))
        ).one()
        persisted = db.get(Feedback, first_id)
        check(
            "SQLAlchemy feedback user relationship works",
            persisted is not None and persisted.user.id == normal_user_id,
        )
    summary_body = summary.json()
    check("feedback summary count matches database", summary_body["count"] == int(expected_count))
    check(
        "feedback summary average matches database",
        abs(summary_body["average_rating"] - float(expected_average)) < 1e-9,
    )

    check(
        "non-admin feedback delete blocked",
        client.delete(f"/feedback/{first_id}", headers=auth(user_token)).status_code == 403,
    )
    deleted = client.delete(f"/feedback/{first_id}", headers=auth(admin_token))
    check("admin can delete feedback through Architecture-approved API", deleted.status_code == 204)
    feedback_ids.remove(first_id)
    with SessionLocal() as db:
        check("deleted feedback no longer exists", db.get(Feedback, first_id) is None)

    print(checks)
    print("STAGE 15 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if feedback_ids:
            for item in list(db.scalars(select(Feedback).where(Feedback.id.in_(feedback_ids))).all()):
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
