from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select, true
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.market import Market
from app.models.payment import Payment
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.admin_summary_schema import AdminSummary
from app.services.price_update_service import _latest_approved_price_statement


def get_admin_summary(db: Session, *, now: datetime | None = None) -> AdminSummary:
    current = now or datetime.now(timezone.utc)
    users = select(
        func.count(User.id).label("users"),
        func.count(User.id).filter(User.is_active.is_(True)).label("active"),
        func.count(User.id).filter(User.created_at >= current-timedelta(days=7)).label("newUsersWeek"),
        func.count(User.id).filter(User.referred_by_id.is_not(None)).label("referralsUsed"),
    ).subquery()
    feedback = select(
        func.count(Feedback.id).label("feedback"),
        func.avg(Feedback.rating).label("average"),
        func.count(Feedback.id).filter(Feedback.is_public_testimonial.is_(True)).label("testimonialsLive"),
    ).subquery()
    payments = select(
        func.count(Payment.id).label("successfulPayments"),
        func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
    ).where(Payment.status == "success").subquery()
    current_ids = _latest_approved_price_statement().with_only_columns(PriceUpdate.id).order_by(None).subquery()
    statement = select(
        users, feedback, payments,
        select(func.count()).select_from(Commodity).scalar_subquery().label("commodities"),
        select(func.count()).select_from(Market).scalar_subquery().label("markets"),
        select(func.count()).select_from(current_ids).scalar_subquery().label("latest"),
        select(func.count()).select_from(PriceUpdate).where(PriceUpdate.is_outdated.is_(True)).scalar_subquery().label("outdated"),
        select(func.count()).select_from(Subscription).where(
            Subscription.status == "trial",
            or_(Subscription.trial_ends_at.is_(None), Subscription.trial_ends_at > current),
        ).scalar_subquery().label("trial"),
    ).select_from(users).join(feedback, true()).join(payments, true())
    # One read statement gives a consistent PostgreSQL snapshot without loading
    # customer records, source identities, screenshots or payment rows into Python.
    # Preserve the original all-successful-payment revenue definition/currency
    # policy. Normal authentication/subscription workflows still handle expiry.
    return AdminSummary(**db.execute(statement).one()._mapping)
