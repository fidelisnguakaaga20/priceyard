from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AdminMetricsResponse(BaseModel):
    generated_at: datetime
    users_total: int
    users_active: int
    users_new_seven_days: int
    users_referred: int
    commodities_total: int
    commodities_active: int
    markets_total: int
    markets_active: int
    prices_total: int
    prices_current: int
    prices_pending: int
    prices_approved: int
    prices_rejected: int
    prices_withdrawn: int
    prices_outdated: int
    open_flags: int
    flagged_prices: int
    subscription_statuses: dict[str, int]
    valid_trial_subscriptions: int
    valid_paid_subscriptions: int
    feedback_count: int
    feedback_average_rating: Decimal | None
    testimonials_live: int
    payments_total: int
    payments_pending: int
    payments_failed: int
    payments_recorded_success: int
    payments_provider_confirmed: int
    payments_access_applied: int
    payments_requires_review: int
    recorded_success_amount_ngn: Decimal
    recorded_success_amounts: dict[str, Decimal]
