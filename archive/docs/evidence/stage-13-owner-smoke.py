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
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.subscription import Subscription
from app.models.user import User
from app.models.watchlist import Watchlist

client = TestClient(app)
SessionLocal = get_session_factory()
run_id = uuid4().hex
password = "Stage13-Test-Password!"
user1_email = f"stage13-user1-{run_id}@example.com"
user2_email = f"stage13-user2-{run_id}@example.com"
checks: dict[str, str] = {}
user_ids: list[int] = []
watchlist_ids: list[int] = []


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    checks[name] = "PASS"


def register(name: str, email: str) -> int:
    response = client.post(
        "/auth/register",
        json={"full_name": name, "email": email, "password": password},
    )
    check(f"registration works for {email}", response.status_code == 201)
    user_id = response.json()["id"]
    user_ids.append(user_id)
    return user_id


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
        check("Stage 13 watchlists migration applied", "watchlists" in tables)
        columns = {item["name"] for item in inspector.get_columns("watchlists")}
        check(
            "watchlists approved fields exist",
            {
                "user_id",
                "commodity_id",
                "market_id",
                "target_price",
                "created_at",
                "updated_at",
            }.issubset(columns),
        )

        commodities = {
            item.name: item.id
            for item in db.scalars(
                select(Commodity).where(Commodity.name.in_(["Egusi", "Beans", "Palm oil"]))
            ).all()
        }
        check("Stage 6 Egusi commodity exists", "Egusi" in commodities)
        check("Stage 6 Beans commodity exists", "Beans" in commodities)
        check("Stage 6 Palm oil commodity exists", "Palm oil" in commodities)

        nasarawa = db.scalar(select(Market).where(Market.name == "Nasarawa"))
        check("Stage 6 Nasarawa market exists", nasarawa is not None)
        nasarawa_id = nasarawa.id

    user1_id = register("Stage 13 User One", user1_email)
    user2_id = register("Stage 13 User Two", user2_email)
    user1_token = login(user1_email)
    user2_token = login(user2_email)

    check("unauthenticated watchlist access blocked", client.get("/watchlist").status_code == 401)

    created_by_name: dict[str, int] = {}
    for commodity_name in ("Egusi", "Beans", "Palm oil"):
        response = client.post(
            "/watchlist",
            json={"commodity_id": commodities[commodity_name]},
            headers=auth(user1_token),
        )
        check(f"save {commodity_name} works", response.status_code == 201)
        body = response.json()
        watchlist_ids.append(body["id"])
        created_by_name[commodity_name] = body["id"]
        check(f"{commodity_name} belongs to current user", body["user_id"] == user1_id)
        check(f"{commodity_name} commodity saved", body["commodity_id"] == commodities[commodity_name])
        check(f"{commodity_name} market is optional", body["market_id"] is None)
        check(f"{commodity_name} response does not expose deferred target price", "target_price" not in body)

    market_response = client.post(
        "/watchlist",
        json={"market_id": nasarawa_id},
        headers=auth(user1_token),
    )
    check("save market works", market_response.status_code == 201)
    market_item_id = market_response.json()["id"]
    watchlist_ids.append(market_item_id)
    check("saved market belongs to current user", market_response.json()["user_id"] == user1_id)
    check("Nasarawa market saved", market_response.json()["market_id"] == nasarawa_id)

    both_response = client.post(
        "/watchlist",
        json={"commodity_id": commodities["Egusi"], "market_id": nasarawa_id},
        headers=auth(user1_token),
    )
    check("save commodity and market together works", both_response.status_code == 201)
    both_item_id = both_response.json()["id"]
    watchlist_ids.append(both_item_id)

    check(
        "empty watchlist item rejected",
        client.post("/watchlist", json={}, headers=auth(user1_token)).status_code == 422,
    )
    check(
        "deferred target price input rejected",
        client.post(
            "/watchlist",
            json={"commodity_id": commodities["Egusi"], "target_price": "200000.00"},
            headers=auth(user1_token),
        ).status_code == 422,
    )

    duplicate = client.post(
        "/watchlist",
        json={"commodity_id": commodities["Egusi"]},
        headers=auth(user1_token),
    )
    check("duplicate handling works", duplicate.status_code == 409)

    own_list = client.get("/watchlist", headers=auth(user1_token))
    check("own watchlist works", own_list.status_code == 200)
    own_ids = {item["id"] for item in own_list.json()}
    check("own list contains saved items", set(watchlist_ids).issubset(own_ids))
    check("own list contains only current user items", all(item["user_id"] == user1_id for item in own_list.json()))

    user2_list = client.get("/watchlist", headers=auth(user2_token))
    check("second user has isolated list", user2_list.status_code == 200 and user2_list.json() == [])

    check(
        "cross-user removal blocked",
        client.delete(f"/watchlist/{created_by_name['Egusi']}", headers=auth(user2_token)).status_code == 404,
    )

    remove = client.delete(f"/watchlist/{created_by_name['Beans']}", headers=auth(user1_token))
    check("watchlist removal works", remove.status_code == 204)
    watchlist_ids.remove(created_by_name["Beans"])
    after_remove = client.get("/watchlist", headers=auth(user1_token))
    check(
        "removed item no longer appears",
        created_by_name["Beans"] not in {item["id"] for item in after_remove.json()},
    )

    with SessionLocal() as db:
        persisted = db.scalar(
            select(Watchlist).where(
                Watchlist.user_id == user1_id,
                Watchlist.commodity_id == commodities["Egusi"],
                Watchlist.market_id.is_(None),
            )
        )
        check("SQLAlchemy user/commodity watchlist relationship works", persisted is not None)
        user = db.get(User, user1_id)
        check(
            "SQLAlchemy user own-watchlist relationship works",
            user is not None and any(item.id == persisted.id for item in user.watchlist_items),
        )

    print(checks)
    print("STAGE 13 OWNER SMOKE: PASS")
finally:
    with SessionLocal() as db:
        if user_ids:
            for item in list(db.scalars(select(Watchlist).where(Watchlist.user_id.in_(user_ids))).all()):
                db.delete(item)
            db.commit()

        for user_id in user_ids:
            subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
            if subscription is not None:
                db.delete(subscription)
            user = db.get(User, user_id)
            if user is not None:
                db.delete(user)
        db.commit()
