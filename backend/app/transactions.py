"""HTTP transaction ownership and complete sanitized administrative auditing."""
from __future__ import annotations

from sqlalchemy import event, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database import AtomicSession


@event.listens_for(AtomicSession, "before_flush")
def remember_changes(db, _context, _instances):
    from app.models.audit_log import AuditLog
    from app.services.audit_service import snapshot_model, sanitize_audit_value
    explicit = db.info.setdefault("explicit_audits", set())
    for item in db.new:
        if isinstance(item, AuditLog):
            explicit.add((item.table_name, item.record_id))
    changes = db.info.setdefault("mutation_snapshots", {})
    excluded = {"audit_logs", "auth_sessions", "email_verification_tokens", "password_reset_tokens", "notification_jobs", "activity_events"}
    for collection, operation in ((db.new, "create"), (db.dirty, "edit"), (db.deleted, "delete")):
        for item in list(collection):
            table = getattr(item, "__tablename__", None)
            if not table or table in excluded or (operation == "edit" and not db.is_modified(item, include_collections=False)):
                continue
            key = id(item)
            if key in changes:
                continue
            old = None if operation == "create" else snapshot_model(item)
            if old is not None:
                for attr in inspect(item).mapper.column_attrs:
                    history = inspect(item).attrs[attr.key].history
                    if history.deleted and attr.key in old:
                        old[attr.key] = history.deleted[0]
                old = sanitize_audit_value(old)
            changes[key] = (item, table, operation, old)


def complete_audits(db: AtomicSession) -> None:
    from app.models.audit_log import AuditLog
    from app.services.audit_service import snapshot_model
    actor_id = db.info.get("actor_id")
    if not actor_id or db.info.get("actor_role") != "admin":
        return
    db.flush()
    explicit = db.info.get("explicit_audits", set())
    for item, table, operation, old in list(db.info.get("mutation_snapshots", {}).values()):
        record_id = getattr(item, "id", None)
        if (table, record_id) in explicit:
            continue
        db.add(AuditLog(user_id=actor_id, action=f"{table}.{operation}", table_name=table,
                        record_id=record_id, old_value=old,
                        new_value=None if operation == "delete" else snapshot_model(item)))
    db.flush()


def install_transactions(app) -> None:
    """Own one transaction per request, independently of router implementation."""
    app.add_middleware(TransactionMiddleware)


class TransactionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        state = scope.setdefault("state", {})
        replaced = False

        async def transactional_send(message):
            nonlocal replaced
            if replaced:
                return
            if message["type"] == "http.response.start":
                db = state.get("database_session")
                if db is not None:
                    try:
                        if message["status"] < 400:
                            complete_audits(db)
                            Session.commit(db)
                        else:
                            Session.rollback(db)
                    except SQLAlchemyError:
                        Session.rollback(db)
                        replaced = True
                        response = JSONResponse(status_code=503, content={"detail": "The request could not be completed. Please retry."})
                        await response(scope, receive, send)
                        return
            await send(message)

        try:
            await self.app(scope, receive, transactional_send)
        except BaseException:
            db = state.get("database_session")
            if db is not None:
                Session.rollback(db)
            raise
        finally:
            db = state.get("database_session")
            if db is not None:
                # No writes from streaming generators or response background
                # tasks are persisted after the response transaction closes.
                Session.rollback(db)
                db.close()
