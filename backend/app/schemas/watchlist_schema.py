from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WatchlistCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commodity_id: int | None = Field(default=None, gt=0)
    market_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def require_selection(self) -> "WatchlistCreate":
        if self.commodity_id is None and self.market_id is None:
            raise ValueError("At least one of commodity_id or market_id is required")
        return self


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    commodity_id: int | None
    market_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
