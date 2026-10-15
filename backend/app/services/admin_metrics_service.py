"""Bounded aggregate queries; never download records to compute dashboard totals."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.feedback import Feedback
from app.models.market import Market
from app.models.payment import Payment
from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.admin_metrics_schema import AdminMetricsResponse
from app.services.price_update_service import count_latest_approved_price_updates


def _count_if(condition):
    return func.coalesce(func.sum(case((condition, 1), else_=0)), 0)


def get_admin_metrics(db: Session, *, now: datetime | None = None) -> AdminMetricsResponse:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Metrics time must include a timezone")
    current = current.astimezone(timezone.utc)
    users = db.execute(select(
        func.count(User.id).label("total"), _count_if(User.is_active.is_(True)).label("active"),
        _count_if(and_(User.created_at >= current - timedelta(days=7), User.created_at <= current)).label("new"),
        _count_if(User.referred_by_id.is_not(None)).label("referred"),
    )).one()
    commodities = db.execute(select(func.count(Commodity.id), _count_if(Commodity.is_active.is_(True)))).one()
    markets = db.execute(select(func.count(Market.id), _count_if(Market.is_active.is_(True)))).one()
    prices = db.execute(select(
        func.count(PriceUpdate.id).label("total"), _count_if(PriceUpdate.status == "pending").label("pending"),
        _count_if(PriceUpdate.status == "approved").label("approved"),
        _count_if(PriceUpdate.status == "rejected").label("rejected"),
        _count_if(PriceUpdate.status == "withdrawn").label("withdrawn"),
        _count_if(PriceUpdate.is_outdated.is_(True)).label("outdated"),
    )).one()

    # These are effective-access counts, independent of stale stored labels.
    # Legacy date-only expiry includes that complete UTC date.
    paid_valid = and_(Subscription.status.in_(("active", "cancelled")), or_(
        Subscription.manual_grant.is_(True), Subscription.paid_expires_at > current,
        and_(Subscription.paid_expires_at.is_(None), Subscription.end_date >= current.date()),
        and_(Subscription.status == "active", Subscription.paid_expires_at.is_(None), Subscription.end_date.is_(None)),
    ))
    trial_valid = and_(Subscription.status == "trial", Subscription.trial_ends_at > current)
    subscription_rows = db.execute(select(
        Subscription.status, func.count(Subscription.id),
        _count_if(and_(User.is_active.is_(True), trial_valid)),
        _count_if(and_(User.is_active.is_(True), paid_valid)),
    ).join(User, User.id == Subscription.user_id).group_by(Subscription.status)).all()
    statuses = dict.fromkeys(("free", "trial", "active", "expired", "cancelled"), 0)
    valid_trials = valid_paid = 0
    for label, count, trials, paid in subscription_rows:
        statuses[label] = int(count)
        valid_trials += int(trials)
        valid_paid += int(paid)

    feedback = db.execute(select(
        func.count(Feedback.id), func.coalesce(func.sum(Feedback.rating), 0),
        _count_if(Feedback.is_public_testimonial.is_(True)),
    )).one()
    average = (Decimal(feedback[1]) / Decimal(feedback[0])).quantize(Decimal("0.01")) if feedback[0] else None
    flags = db.execute(select(
        _count_if(PriceFlag.resolved.is_(False)),
        func.count(func.distinct(case((PriceFlag.resolved.is_(False), PriceFlag.price_update_id), else_=None))),
    )).one()
    payments = db.execute(select(
        func.count(Payment.id).label("total"), _count_if(Payment.status == "pending").label("pending"),
        _count_if(Payment.status == "failed").label("failed"),
        _count_if(Payment.status == "success").label("recorded_success"),
        _count_if(Payment.confirmed_at.is_not(None)).label("confirmed"),
        _count_if(or_(Payment.entitlement_applied_at.is_not(None), Payment.reconciliation_resolution == "already_applied")).label("applied"),
        _count_if(Payment.requires_reconciliation.is_(True)).label("review"),
    )).one()
    # Stored success is evidence of a recorded state, not independent proof of
    # settlement/refunds. Keep currencies separate and never infer old activation.
    amounts = {
        currency: Decimal(amount).quantize(Decimal("0.01"))
        for currency, amount in db.execute(select(Payment.currency, func.sum(Payment.amount))
            .where(Payment.status == "success").group_by(Payment.currency)).all()
    }
    return AdminMetricsResponse(
        generated_at=current, users_total=users.total, users_active=users.active,
        users_new_seven_days=users.new, users_referred=users.referred,
        commodities_total=commodities[0], commodities_active=commodities[1],
        markets_total=markets[0], markets_active=markets[1],
        prices_total=prices.total, prices_current=count_latest_approved_price_updates(db),
        prices_pending=prices.pending, prices_approved=prices.approved, prices_rejected=prices.rejected,
        prices_withdrawn=prices.withdrawn, prices_outdated=prices.outdated,
        open_flags=flags[0], flagged_prices=flags[1], subscription_statuses=statuses,
        valid_trial_subscriptions=valid_trials, valid_paid_subscriptions=valid_paid,
        feedback_count=feedback[0], feedback_average_rating=average, testimonials_live=feedback[2],
        payments_total=payments.total, payments_pending=payments.pending, payments_failed=payments.failed,
        payments_recorded_success=payments.recorded_success, payments_provider_confirmed=payments.confirmed,
        payments_access_applied=payments.applied, payments_requires_review=payments.review,
        recorded_success_amount_ngn=amounts.get("NGN", Decimal("0.00")), recorded_success_amounts=amounts,
    )
