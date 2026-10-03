from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
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


def apply_paid_expiry(subscription: Subscription, *, now: datetime | None = None) -> bool:
    """Expire a paid subscription once its end_date passes. A manually-activated
    (admin) subscription has end_date=None and never expires this way - only
    payment-driven activations (which set a real end_date) are affected."""
    if subscription.status != "active" or subscription.end_date is None:
        return False

    current_date = (now or utc_now()).date()
    if current_date <= subscription.end_date:
        return False

    subscription.status = "expired"
    if subscription.user.role != "admin":
        subscription.user.role = "free_user"
    return True


def expire_trial_if_needed(db: Session, subscription: Subscription, *, now: datetime | None = None) -> Subscription:
    trial_changed = apply_trial_expiry(subscription, now=now)
    paid_changed = apply_paid_expiry(subscription, now=now)
    if trial_changed or paid_changed:
        db.commit()
        db.refresh(subscription)
    return subscription


def has_full_access(subscription: Subscription, *, now: datetime | None = None) -> bool:
    if subscription.status == "active":
        if subscription.end_date is None:
            return True
        current_date = (now or utc_now()).date()
        return current_date <= subscription.end_date
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
    changed = any(apply_trial_expiry(item, now=now) | apply_paid_expiry(item, now=now) for item in subscriptions)
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


PAID_PLAN_DURATIONS_DAYS = {"monthly": 30, "seasonal": 90}


def activate_paid_subscription(db: Session, subscription: Subscription, *, plan: str, now: datetime | None = None) -> Subscription:
    """Activate paid access for a completed payment. Distinct from
    update_subscription_status's "active" branch (used for manual admin grants,
    which stay indefinite/end_date=None) - a payment always has a real
    end_date matching what was actually paid for."""
    current_time = now or utc_now()
    duration_days = PAID_PLAN_DURATIONS_DAYS[plan]
    subscription.plan_name = f"paid_{plan}"
    subscription.status = "active"
    subscription.start_date = current_time.date()
    subscription.end_date = current_time.date() + timedelta(days=duration_days)
    if subscription.user.role != "admin":
        subscription.user.role = "paid_user"
    db.commit()
    db.refresh(subscription)
    return subscription


REFERRAL_REWARD_DAYS = 7


def apply_referral_reward(db: Session, referrer: User) -> bool:
    """Extend the referrer's trial when someone they referred registers. Only applies
    to trial/free accounts - active/expired/cancelled subscriptions are left untouched
    since extra "trial days" has no meaning for them."""
    subscription = find_subscription_for_user(db, referrer.id)
    if subscription is None:
        return False

    now = utc_now()
    if subscription.status == "trial":
        current_end = subscription.trial_ends_at or now
        if current_end.tzinfo is None:
            current_end = current_end.replace(tzinfo=timezone.utc)
        subscription.trial_ends_at = max(current_end, now) + timedelta(days=REFERRAL_REWARD_DAYS)
    elif subscription.status == "free":
        subscription.plan_name = "trial"
        subscription.status = "trial"
        subscription.trial_started_at = now
        subscription.trial_ends_at = now + timedelta(days=REFERRAL_REWARD_DAYS)
    else:
        return False

    db.commit()
    db.refresh(subscription)
    return True


TRIAL_REMINDER_WINDOW_DAYS = 3


def send_trial_expiry_reminders(db: Session) -> int:
    """Email trial users whose trial ends within the reminder window, once each."""
    from app.services.email_service import send_email

    settings = get_settings()
    dashboard_url = f"{settings.frontend_url.rstrip('/')}/dashboard"
    now = utc_now()
    window_end = now + timedelta(days=TRIAL_REMINDER_WINDOW_DAYS)
    candidates = db.scalars(
        select(Subscription).where(
            Subscription.status == "trial",
            Subscription.trial_ends_at.is_not(None),
            Subscription.trial_ends_at <= window_end,
            Subscription.trial_ends_at > now,
            Subscription.trial_reminder_sent_at.is_(None),
        )
    ).all()

    sent = 0
    for subscription in candidates:
        user = subscription.user
        if not user.is_active:
            continue
        days_left = max((subscription.trial_ends_at - now).days, 0)
        subject = f"Your PriceYard trial ends in {days_left} day(s) — keep your full access"
        body = (
            f"Hi {user.full_name},\n\n"
            f"Your 14-day PriceYard trial ends in {days_left} day(s). After it ends, "
            "you'll lose access to price history, buying zones, sell-watch windows, "
            "and storage suitability -- back to limited free access only.\n\n"
            "To keep full access, upgrade now from your dashboard:\n"
            f"{dashboard_url}\n\n"
            "Plans: NGN 2,500/month, or NGN 6,000/3 months.\n\n"
            "PriceYard — Know the market before you buy or sell."
        )
        try:
            send_email(recipient=user.email, subject=subject, body=body)
        except Exception:
            continue
        subscription.trial_reminder_sent_at = now
        sent += 1

    if sent:
        db.commit()
    return sent
