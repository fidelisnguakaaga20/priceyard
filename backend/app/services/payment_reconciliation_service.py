"""Bounded recovery of recorded purchases; no charging or background startup."""
from contextlib import contextmanager
import math
import time

from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.payment import Payment
from app.models.user import User
from app.services.payment_service import verify_recorded_payment


@contextmanager
def _single_worker(engine: Engine, apply: bool):
    if not apply or engine.dialect.name != "postgresql":
        # SQLite is used only by single-process synthetic tests/preview.
        yield True
        return
    with engine.connect() as connection:
        acquired = False
        try:
            acquired = connection.execute(text("SELECT pg_try_advisory_lock(741523, 3)")).scalar_one()
            connection.commit()
            yield acquired
        finally:
            if acquired:
                try:
                    connection.rollback()
                    connection.execute(text("SELECT pg_advisory_unlock(741523, 3)"))
                    connection.commit()
                except BaseException:
                    # Never return a connection retaining a session lock to its pool.
                    connection.invalidate()
                    raise


def reconcile_payments(engine: Engine, *, apply: bool = False, limit: int = 25,
                       after_id: int = 0, ceiling_id: int | None = None,
                       time_budget_seconds: float = 45) -> dict:
    """One serial, resumable page. Default dry run never verifies or changes rows.

    Only pending/failed recorded purchases qualify. Existing evidence validation,
    locking, activation, purchased-time preservation and audit logic are reused.
    Successful legacy purchases are never re-credited or automatically repaired.
    """
    if (type(apply) is not bool or type(limit) is not int or not 1 <= limit <= 100
            or type(after_id) is not int or after_id < 0
            or (ceiling_id is not None and (type(ceiling_id) is not int or ceiling_id < after_id))
            or type(time_budget_seconds) not in (int, float)
            or not math.isfinite(time_budget_seconds) or not 0 < time_budget_seconds <= 300):
        raise ValueError("Invalid reconciliation bounds")
    report = {"dry_run": not apply, "busy": False, "complete": False,
              "ceiling_id": ceiling_id, "next_after_id": after_id, "outcomes": []}
    started = time.monotonic()
    with _single_worker(engine, apply) as acquired:
        if not acquired:
            report["busy"] = True
            return report
        with Session(engine, autoflush=False) as db:
            ceiling = ceiling_id
            if ceiling is None:
                ceiling = db.scalar(select(Payment.id).order_by(Payment.id.desc()).limit(1)) or 0
            report["ceiling_id"] = ceiling
            candidates = list(db.scalars(select(Payment.id).where(
                Payment.status.in_(("pending", "failed")), Payment.id > after_id, Payment.id <= ceiling,
            ).order_by(Payment.id).limit(limit)))
        last_id = after_id
        for payment_id in candidates:
            if time.monotonic() - started >= time_budget_seconds:
                break
            outcome = "candidate"
            if apply:
                with Session(engine, autoflush=False, expire_on_commit=False) as db:
                    try:
                        payment = db.get(Payment, payment_id)
                        owner = db.get(User, payment.user_id) if payment is not None else None
                        if payment is None or owner is None:
                            outcome = "missing_record"
                        else:
                            result = verify_recorded_payment(db, owner, payment.reference)
                            outcome = "confirmed" if result.status == "success" else "unconfirmed"
                    except Exception:
                        db.rollback()
                        # Approved manual-grant holds commit evidence before409.
                        held = db.scalar(select(AuditLog.id).where(
                            AuditLog.action == "payment.review_required", AuditLog.table_name == "payments",
                            AuditLog.record_id == payment_id,
                        ).limit(1))
                        outcome = "review_required" if held is not None else "error"
            report["outcomes"].append({"payment_id": payment_id, "outcome": outcome})
            last_id = payment_id
        with Session(engine, autoflush=False) as db:
            remaining = db.scalar(select(Payment.id).where(
                Payment.status.in_(("pending", "failed")), Payment.id > last_id, Payment.id <= ceiling,
            ).order_by(Payment.id).limit(1))
        report["complete"] = remaining is None
        report["next_after_id"] = 0 if report["complete"] else last_id
    return report
