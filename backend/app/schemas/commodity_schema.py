from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_image_url(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    if not (value.startswith("http://") or value.startswith("https://")):
        raise ValueError("Image URL must start with http:// or https://")
    return value


class CommodityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    is_upcoming: bool = False
    expected_available_date: date | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str | None) -> str | None:
        return _validate_image_url(value)


class CommodityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    is_upcoming: bool | None = None
    expected_available_date: date | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str | None) -> str | None:
        return _validate_image_url(value)


class CommodityResponse(BaseModel):
    id: int
    name: str
    description: str | None
    image_url: str | None
    is_active: bool
    is_upcoming: bool
    expected_available_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
