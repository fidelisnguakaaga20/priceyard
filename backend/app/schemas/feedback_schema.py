from __future__ import annotations

import base64
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_SCREENSHOT_BYTES = 2 * 1024 * 1024  # 2MB, decoded


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)
    price_usefulness: str | None = Field(default=None, max_length=500)
    price_accuracy: str | None = Field(default=None, max_length=500)
    missing_market_request: str | None = Field(default=None, max_length=500)
    missing_commodity_request: str | None = Field(default=None, max_length=500)
    complaint_or_suggestion: str | None = Field(default=None, max_length=5000)
    continue_using_feedback: bool | None = None
    willingness_to_pay_feedback: bool | None = None
    screenshot_data: str | None = Field(default=None, max_length=2_796_250)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("screenshot_data")
    @classmethod
    def validate_screenshot(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        prefixes = {"data:image/png;base64": b"\x89PNG\r\n\x1a\n", "data:image/jpeg;base64": b"\xff\xd8\xff", "data:image/webp;base64": b"RIFF"}
        try:
            prefix, encoded = value.split(",", 1)
            if prefix not in prefixes:
                raise ValueError("Only PNG, JPEG and WebP screenshots are supported")
            raw = base64.b64decode(encoded, validate=True)
            if not raw.startswith(prefixes[prefix]) or (prefix.endswith("webp;base64") and raw[8:12] != b"WEBP"):
                raise ValueError("Screenshot format does not match its image type")
        except Exception as exc:
            raise ValueError("Screenshot data is not valid") from exc
        if len(raw) > MAX_SCREENSHOT_BYTES:
            raise ValueError("Screenshot must be smaller than 2MB")
        return value


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: str | None
    price_usefulness: str | None
    price_accuracy: str | None
    missing_market_request: str | None
    missing_commodity_request: str | None
    complaint_or_suggestion: str | None
    continue_using_feedback: bool | None
    willingness_to_pay_feedback: bool | None
    is_public_testimonial: bool
    testimonial_display_name: str | None
    screenshot_data: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackSummaryResponse(BaseModel):
    count: int
    average_rating: float | None


class TestimonialPublishRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class TestimonialResponse(BaseModel):
    id: int
    rating: int
    quote: str
    display_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
