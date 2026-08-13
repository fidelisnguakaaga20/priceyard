from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackSummaryResponse(BaseModel):
    count: int
    average_rating: float | None
