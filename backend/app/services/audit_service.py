from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import inspect as sa_inspect, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User

SENSITIVE_KEY_FRAGMENTS = (
    "password",
    "secret",
    "token",
    "authorization",
    "database_url",
    "database_password",
    ".env",
)
# Price-source identities are intentionally excluded from audit snapshots.
# They are operationally private and are not required by Stage 16 audit proof.
PRIVATE_AUDIT_FIELDS = {"source_1", "source_2"}


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return key in PRIVATE_AUDIT_FIELDS or any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
            if not _is_sensitive_key(str(key))
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


def sanitize_audit_value(value: dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    if value is None:
        return None
    safe = _json_safe(value)
    if not isinstance(safe, (dict, list)):
        raise TypeError("Audit values must be dictionaries, lists, or null")
    return safe


def snapshot_model(model: Any, *, extra_exclude: set[str] | None = None) -> dict[str, Any]:
    excluded = set(extra_exclude or set()) | PRIVATE_AUDIT_FIELDS
    mapper = sa_inspect(model).mapper
    data: dict[str, Any] = {}
    for attr in mapper.column_attrs:
        key = attr.key
        if key in excluded or _is_sensitive_key(key):
            continue
        data[key] = _json_safe(getattr(model, key))
    return data


def create_audit_log(
    db: Session,
    *,
    actor: User,
    action: str,
    table_name: str,
    record_id: int | None,
    old_value: dict[str, Any] | list[Any] | None = None,
    new_value: dict[str, Any] | list[Any] | None = None,
) -> AuditLog:
    item = AuditLog(
        user_id=actor.id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=sanitize_audit_value(old_value),
        new_value=sanitize_audit_value(new_value),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_audit_logs(db: Session) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())).all())


def get_audit_log(db: Session, audit_log_id: int) -> AuditLog:
    item = db.get(AuditLog, audit_log_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return item
