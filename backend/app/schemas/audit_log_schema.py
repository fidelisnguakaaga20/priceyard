from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer

from app.services.audit_service import sanitize_audit_value


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int | None
    old_value: dict[str, Any] | list[Any] | None
    new_value: dict[str, Any] | list[Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("old_value", "new_value")
    def public_audit_value(self, value: dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
        # Older stored logs may predate write-time filtering. Redact only the
        # serialized copy; retain original historical evidence in the database.
        return sanitize_audit_value(value)
