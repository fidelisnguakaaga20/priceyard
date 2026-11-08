"""Safely reverse Stage 19 manual-browser data mutations made by one temporary admin.

This helper is intentionally narrow. It only reverses audited mutations that were
part of the approved Stage 19 browser verification flow: users/subscriptions,
commodities, and markets. It refuses to proceed if that temporary admin made any
other mutating action so that unrelated business data is never guessed at or
silently rewritten.
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if not (BACKEND / ".env").exists():
    raise SystemExit("FAIL: backend/.env is missing. Copy it from the previous stage first.")
os.chdir(BACKEND)
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.database import get_session_factory  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.commodity import Commodity  # noqa: E402
from app.models.market import Market  # noqa: E402
from app.models.subscription import Subscription  # noqa: E402
from app.models.user import User  # noqa: E402

ALLOWED_ACTIONS = {
    "user.update",
    "subscription.user_management_sync",
    "commodity.create",
    "commodity.edit",
    "commodity.delete",
    "market.create",
    "market.edit",
    "market.delete",
}

REQUIRED_COMMODITIES = ("Egusi", "Beans", "Palm oil")
REQUIRED_MARKETS = ("Abuja/FCT", "Kwali Market", "Nasarawa", "Benue")


def parse_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


def restore_user(target: User, old: dict[str, Any]) -> None:
    # Stage 19 user management can change only role and active status.
    if "role" in old:
        target.role = str(old["role"])
    if "is_active" in old:
        target.is_active = bool(old["is_active"])


def restore_subscription(target: Subscription, old: dict[str, Any]) -> None:
    for field in ("plan_name", "status", "payment_reference"):
        if field in old:
            setattr(target, field, old[field])
    for field in ("trial_started_at", "trial_ends_at"):
        if field in old:
            setattr(target, field, parse_dt(old[field]))
    for field in ("start_date", "end_date"):
        if field in old:
            setattr(target, field, parse_date(old[field]))


def restore_commodity(target: Commodity, old: dict[str, Any]) -> None:
    for field in ("name", "description", "is_active"):
        if field in old:
            setattr(target, field, old[field])


def recreate_commodity(old: dict[str, Any]) -> Commodity:
    return Commodity(
        id=int(old["id"]),
        name=str(old["name"]),
        description=old.get("description"),
        is_active=bool(old.get("is_active", True)),
        created_at=parse_dt(old.get("created_at")) or datetime.now().astimezone(),
        updated_at=parse_dt(old.get("updated_at")) or datetime.now().astimezone(),
    )


def restore_market(target: Market, old: dict[str, Any]) -> None:
    for field in ("name", "state", "country", "market_day", "description", "is_active"):
        if field in old:
            setattr(target, field, old[field])


def recreate_market(old: dict[str, Any]) -> Market:
    return Market(
        id=int(old["id"]),
        name=str(old["name"]),
        state=old.get("state"),
        country=str(old.get("country") or "Nigeria"),
        market_day=old.get("market_day"),
        description=old.get("description"),
        is_active=bool(old.get("is_active", True)),
        created_at=parse_dt(old.get("created_at")) or datetime.now().astimezone(),
        updated_at=parse_dt(old.get("updated_at")) or datetime.now().astimezone(),
    )


def names_casefold(rows: list[Any]) -> set[str]:
    return {str(row.name).strip().casefold() for row in rows}


def require_core_data(db) -> None:
    commodities = list(db.scalars(select(Commodity).order_by(Commodity.id)).all())
    markets = list(db.scalars(select(Market).order_by(Market.id)).all())
    commodity_names = names_casefold(commodities)
    market_names = names_casefold(markets)
    missing_commodities = [x for x in REQUIRED_COMMODITIES if x.casefold() not in commodity_names]
    missing_markets = [x for x in REQUIRED_MARKETS if x.casefold() not in market_names]
    if missing_commodities or missing_markets:
        parts = []
        if missing_commodities:
            parts.append("missing commodities: " + ", ".join(missing_commodities))
        if missing_markets:
            parts.append("missing markets: " + ", ".join(missing_markets))
        raise RuntimeError("Core-data verification failed after rollback: " + "; ".join(parts))


def reverse_one(db, log: AuditLog) -> str:
    old = log.old_value if isinstance(log.old_value, dict) else {}
    action = log.action
    rid = log.record_id

    if action == "user.update":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} user.update has no record id")
        target = db.get(User, rid)
        if target is None:
            raise RuntimeError(f"audit #{log.id}: user #{rid} no longer exists")
        restore_user(target, old)
        return f"audit #{log.id}: restored user #{rid}"

    if action == "subscription.user_management_sync":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} subscription sync has no record id")
        target = db.get(Subscription, rid)
        if target is None:
            raise RuntimeError(f"audit #{log.id}: subscription #{rid} no longer exists")
        restore_subscription(target, old)
        return f"audit #{log.id}: restored subscription #{rid}"

    if action == "commodity.create":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} commodity.create has no record id")
        target = db.get(Commodity, rid)
        if target is not None:
            db.delete(target)
            db.flush()  # Let PostgreSQL block unsafe deletion through foreign keys.
        return f"audit #{log.id}: removed test-created commodity #{rid}"

    if action == "commodity.edit":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} commodity.edit has no record id")
        target = db.get(Commodity, rid)
        if target is None:
            raise RuntimeError(f"audit #{log.id}: commodity #{rid} no longer exists")
        restore_commodity(target, old)
        return f"audit #{log.id}: restored commodity #{rid}"

    if action == "commodity.delete":
        if rid is None or not old:
            raise RuntimeError(f"audit #{log.id} commodity.delete is missing its old snapshot")
        target = db.get(Commodity, rid)
        if target is None:
            db.add(recreate_commodity(old))
            db.flush()
        else:
            restore_commodity(target, old)
        return f"audit #{log.id}: restored deleted commodity #{rid}"

    if action == "market.create":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} market.create has no record id")
        target = db.get(Market, rid)
        if target is not None:
            db.delete(target)
            db.flush()  # Let PostgreSQL block unsafe deletion through foreign keys.
        return f"audit #{log.id}: removed test-created market #{rid}"

    if action == "market.edit":
        if rid is None:
            raise RuntimeError(f"audit #{log.id} market.edit has no record id")
        target = db.get(Market, rid)
        if target is None:
            raise RuntimeError(f"audit #{log.id}: market #{rid} no longer exists")
        restore_market(target, old)
        return f"audit #{log.id}: restored market #{rid}"

    if action == "market.delete":
        if rid is None or not old:
            raise RuntimeError(f"audit #{log.id} market.delete is missing its old snapshot")
        target = db.get(Market, rid)
        if target is None:
            db.add(recreate_market(old))
            db.flush()
        else:
            restore_market(target, old)
        return f"audit #{log.id}: restored deleted market #{rid}"

    raise RuntimeError(f"Unsupported action {action!r}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python docs/evidence/stage-19-data-repair.py "
            "stage19-browser-admin-...@example.com"
        )
    email = sys.argv[1].strip().lower()
    if not email.startswith("stage19-browser-admin-") or not email.endswith("@example.com"):
        raise SystemExit("FAIL: pass the temporary Stage 19 browser-admin email only")

    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        actor = db.scalar(select(User).where(func.lower(User.email) == email))
        if actor is None:
            raise SystemExit("FAIL: temporary Stage 19 admin was not found; do not guess which audit logs to reverse")

        logs = list(
            db.scalars(
                select(AuditLog)
                .where(AuditLog.user_id == actor.id)
                .order_by(AuditLog.id.desc())
            ).all()
        )
        mutating_logs = [log for log in logs if log.old_value is not None or log.new_value is not None]
        unsupported = [log for log in mutating_logs if log.action not in ALLOWED_ACTIONS]
        if unsupported:
            print("STAGE 19 DATA REPAIR: BLOCKED")
            print("The temporary admin has additional mutating audit actions that this narrow repair will not guess at:")
            for log in unsupported:
                print(f"- audit #{log.id}: {log.action} on {log.table_name} record {log.record_id}")
            raise SystemExit(2)

        print(f"Temporary admin: user #{actor.id}")
        print(f"Audited mutations to reverse: {len(mutating_logs)}")
        if not mutating_logs:
            require_core_data(db)
            print("No reversible Stage 19 manual mutations were found.")
            print("Core-data verification: PASS")
            print("STAGE 19 DATA REPAIR: PASS")
            return

        messages: list[str] = []
        try:
            for log in mutating_logs:
                messages.append(reverse_one(db, log))
            db.flush()
            require_core_data(db)
            db.commit()
        except (IntegrityError, RuntimeError, ValueError, TypeError) as exc:
            db.rollback()
            print("STAGE 19 DATA REPAIR: BLOCKED")
            print(f"No repair changes were committed. Reason: {exc}")
            raise SystemExit(2) from exc

        for message in messages:
            print(message)
        print("Required commodities present: Egusi, Beans, Palm oil")
        print("Required markets present: Abuja/FCT, Kwali Market, Nasarawa, Benue")
        print("Core-data verification: PASS")
        print("STAGE 19 DATA REPAIR: PASS")
        print("Temporary admin and its audit logs were intentionally kept for the remaining browser check.")


if __name__ == "__main__":
    main()
