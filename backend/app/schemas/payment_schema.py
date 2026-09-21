from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

PaymentPlan = Literal["monthly", "seasonal"]


class PaymentInitiateRequest(BaseModel):
    plan: PaymentPlan


class PaymentInitiateResponse(BaseModel):
    authorization_url: str
    reference: str


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    reference: str
    plan: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
