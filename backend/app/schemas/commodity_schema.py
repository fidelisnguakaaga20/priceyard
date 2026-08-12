from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommodityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    is_active: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)


class CommodityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class CommodityResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
