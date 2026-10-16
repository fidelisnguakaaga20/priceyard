from __future__ import annotations

import base64
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_SCREENSHOT_BYTES = 2 * 1024 * 1024  # 2MB, decoded
MAX_SCREENSHOT_ENCODING = 4 * ((MAX_SCREENSHOT_BYTES + 2) // 3)


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    price_usefulness: str | None = None
    price_accuracy: str | None = None
    missing_market_request: str | None = None
    missing_commodity_request: str | None = None
    complaint_or_suggestion: str | None = None
    continue_using_feedback: bool | None = None
    willingness_to_pay_feedback: bool | None = None
    screenshot_data: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("screenshot_data")
    @classmethod
    def validate_screenshot(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not value.startswith("data:image/"):
            raise ValueError("Screenshot must be an image file")
        separator = value.find(",")
        if separator < 0:
            raise ValueError("Screenshot data is not valid")
        # Check length before slicing/decoding an arbitrarily large payload.
        # Keep the original decoded 2MB boundary and image-format policy.
        if len(value) - separator - 1 > MAX_SCREENSHOT_ENCODING:
            raise ValueError("Screenshot must be smaller than 2MB")
        try:
            raw = base64.b64decode(value[separator + 1:], validate=True)
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
