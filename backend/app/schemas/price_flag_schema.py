from datetime import datetime

from pydantic import BaseModel, Field


class PriceFlagCreate(BaseModel):
    reason: str | None = Field(default=None, max_length=50)


class FlaggedPriceSummary(BaseModel):
    price_update_id: int
    commodity_name: str
    market_name: str
    flag_count: int
    latest_flag_at: datetime
