from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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
