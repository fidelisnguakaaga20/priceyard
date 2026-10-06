from datetime import datetime

from pydantic import BaseModel


class PriceFlagCreate(BaseModel):
    reason: str | None = None


class FlaggedPriceSummary(BaseModel):
    price_update_id: int
    commodity_name: str
    market_name: str
    flag_count: int
    latest_flag_at: datetime
