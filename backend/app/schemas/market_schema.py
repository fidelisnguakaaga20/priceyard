from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.commodity_schema import _validate_image_url

MarketDay = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class MarketCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="Nigeria", min_length=1, max_length=100)
    market_day: MarketDay | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str | None) -> str | None:
        return _validate_image_url(value)


class MarketUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    market_day: MarketDay | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str | None) -> str | None:
        return _validate_image_url(value)


class MarketResponse(BaseModel):
    id: int
    name: str
    state: str | None
    country: str
    market_day: MarketDay | None
    description: str | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
