from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.user import User

TRIAL_DURATION_DAYS = 14

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_trial_subscription(*, user: User, now: datetime | None = None) -> Subscription:
    started_at = now or utc_now()
    return Subscription(
        user=user,
        plan_name="trial",
        status="trial",
        trial_started_at=started_at,
        trial_ends_at=started_at + timedelta(days=TRIAL_DURATION_DAYS),
    )


def apply_trial_expiry(subscription: Subscription, *, now: datetime | None = None) -> bool:
    if subscription.status != "trial" or subscription.trial_ends_at is None:
        return False

    current_time = now or utc_now()
    trial_end = subscription.trial_ends_at
    if trial_end.tzinfo is None:
        trial_end = trial_end.replace(tzinfo=timezone.utc)

    if current_time < trial_end:
        return False

    subscription.status = "expired"
    if subscription.user.role != "admin":
        subscription.user.role = "free_user"
    return True


def expire_trial_if_needed(db: Session, subscription: Subscription, *, now: datetime | None = None) -> Subscription:
    if apply_trial_expiry(subscription, now=now):
        db.commit()
        db.refresh(subscription)
    return subscription


def has_full_access(subscription: Subscription, *, now: datetime | None = None) -> bool:
    if subscription.status == "active":
        return True
    if subscription.status != "trial" or subscription.trial_ends_at is None:
        return False

    current_time = now or utc_now()
    trial_end = subscription.trial_ends_at
    if trial_end.tzinfo is None:
        trial_end = trial_end.replace(tzinfo=timezone.utc)
    return current_time < trial_end


def get_subscription_for_user(db: Session, user_id: int) -> Subscription:
    subscription = find_subscription_for_user(db, user_id)
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    return subscription


def find_subscription_for_user(db: Session, user_id: int) -> Subscription | None:
    subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id))
    if subscription is None:
        return None
    return expire_trial_if_needed(db, subscription)


def list_subscriptions(db: Session) -> list[Subscription]:
    subscriptions = list(db.scalars(select(Subscription).order_by(Subscription.id)).all())
    now = utc_now()
    changed = any(apply_trial_expiry(item, now=now) for item in subscriptions)
    if changed:
        db.commit()
        for item in subscriptions:
            db.refresh(item)
    return subscriptions


def update_subscription_status(db: Session, subscription: Subscription, new_status: str) -> Subscription:
    now = utc_now()

    if new_status == "trial":
        subscription.plan_name = "trial"
        subscription.status = "trial"
        subscription.trial_started_at = now
        subscription.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
        subscription.start_date = None
        subscription.end_date = None
        if subscription.user.role != "admin":
            subscription.user.role = "free_user"
    elif new_status == "active":
        subscription.plan_name = "paid"
        subscription.status = "active"
        subscription.start_date = now.date()
        subscription.end_date = None
        if subscription.user.role != "admin":
            subscription.user.role = "paid_user"
    elif new_status == "free":
        subscription.plan_name = "free"
        subscription.status = "free"
        subscription.trial_started_at = None
        subscription.trial_ends_at = None
        subscription.start_date = None
        subscription.end_date = None
        if subscription.user.role != "admin":
            subscription.user.role = "free_user"
    elif new_status == "expired":
        subscription.status = "expired"
        if subscription.user.role != "admin":
            subscription.user.role = "free_user"
    elif new_status == "cancelled":
        subscription.status = "cancelled"
        if subscription.user.role != "admin":
            subscription.user.role = "free_user"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid subscription status",
        )

    db.commit()
    db.refresh(subscription)
    return subscription
