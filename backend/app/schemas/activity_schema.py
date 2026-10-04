from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityPingRequest(BaseModel):
    event_type: str = Field(default="app_visit", max_length=30)
    label: str | None = Field(default=None, max_length=200)


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    label: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivitySummaryResponse(BaseModel):
    unseen_count: int
    recent: list[ActivityEventResponse]
