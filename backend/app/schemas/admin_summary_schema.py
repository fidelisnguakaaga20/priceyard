from decimal import Decimal

from pydantic import BaseModel


class AdminSummary(BaseModel):
    """The fourteen existing dashboard metrics; no account-entry/schema fields."""
    users: int
    commodities: int
    markets: int
    latest: int
    outdated: int
    trial: int
    active: int
    feedback: int
    average: float | None
    newUsersWeek: int
    referralsUsed: int
    testimonialsLive: int
    successfulPayments: int
    revenue: Decimal
