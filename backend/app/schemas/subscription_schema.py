from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

SubscriptionStatus = Literal["free", "trial", "active", "expired", "cancelled"]


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_name: str
    status: SubscriptionStatus
    trial_started_at: datetime | None
    trial_ends_at: datetime | None
    start_date: date | None
    end_date: date | None
    payment_reference: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionStatusUpdate(BaseModel):
    status: SubscriptionStatus
