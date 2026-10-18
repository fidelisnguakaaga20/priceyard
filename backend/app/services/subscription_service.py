from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User
from app.models.audit_log import AuditLog

TRIAL_DURATION_DAYS = 14

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def lock_subscription_state(db: Session, user_id: int) -> tuple[User, Subscription | None]:
    """Match payment/security writers' User -> Subscription row-lock order."""
    user = db.scalar(select(User).where(User.id == user_id).with_for_update().execution_options(populate_existing=True))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    subscription = db.scalar(select(Subscription).where(Subscription.user_id == user_id).with_for_update().execution_options(populate_existing=True))
    return user, subscription


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
    if subscription.user.role not in {"admin", "reporter"}:
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
    if subscription.user.role not in {"admin", "reporter"}:
        subscription.user.role = "free_user"
    return True


def expire_trial_if_needed(db: Session, subscription: Subscription, *, now: datetime | None = None) -> Subscription:
    current_time = now or utc_now()
    trial_end = subscription.trial_ends_at
    if trial_end is not None and trial_end.tzinfo is None:
        trial_end = trial_end.replace(tzinfo=timezone.utc)
    due = (subscription.status == "trial" and trial_end is not None and current_time >= trial_end
           or subscription.status == "active" and subscription.end_date is not None
           and current_time.date() > subscription.end_date)
    if not due:
        return subscription

    # A GET may have read the old expiry just before payment renewed access.
    # Reload under the same User -> Subscription locks as payment/admin writers
    # before changing either row. Do not dirty the stale instance beforehand.
    try:
        with db.no_autoflush:
            _, current = lock_subscription_state(db, subscription.user_id)
        if current is None:
            raise HTTPException(status_code=404, detail="Subscription not found")
        subscription = current
        apply_trial_expiry(subscription, now=current_time)
        apply_paid_expiry(subscription, now=current_time)
        # Release the locks even when a concurrent renewal removed the expiry.
        db.commit()
        db.refresh(subscription)
    except Exception:
        db.rollback()
        raise
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


def expire_subscriptions_for_listing(db: Session) -> None:
    """Keep the original whole-list expiry sweep without loading every account.

    Candidates are bounded, then rechecked under the same User -> Subscription
    locks as payments. A renewal completed while waiting must not be overwritten.
    The sweep commits atomically before any paged/streamed response is produced.
    """
    now = utc_now()
    due = or_(and_(Subscription.status == "trial", Subscription.trial_ends_at <= now),
              and_(Subscription.status == "active", Subscription.end_date < now.date()))
    try:
        ceiling = db.scalar(select(func.max(Subscription.user_id))) or 0
        cursor = 0
        while True:
            users = db.scalars(select(Subscription.user_id).where(
                due, Subscription.user_id > cursor, Subscription.user_id <= ceiling
            ).order_by(Subscription.user_id).limit(100)).all()
            if not users:
                break
            for user_id in users:
                try:
                    _, item = lock_subscription_state(db, user_id)
                except HTTPException as error:
                    if error.status_code == 404:
                        continue  # An account removed after candidate selection.
                    raise
                if item is not None:
                    trial_changed = apply_trial_expiry(item, now=now)
                    paid_changed = apply_paid_expiry(item, now=now)
                    if trial_changed or paid_changed:
                        db.flush()
            cursor = users[-1]
        # Release candidate locks even when a concurrent renewal made them valid.
        db.commit()
    except Exception:
        db.rollback()
        raise


def list_subscriptions(db: Session) -> list[Subscription]:
    # Internal compatibility; HTTP callers use the bounded page/stream paths.
    expire_subscriptions_for_listing(db)
    return list(db.scalars(select(Subscription).order_by(Subscription.id)).all())


def update_subscription_status(db: Session, subscription: Subscription, new_status: str, *, commit: bool = True) -> Subscription:
    now = utc_now()

    if new_status == "trial":
        subscription.plan_name = "trial"
        subscription.status = "trial"
        subscription.trial_started_at = now
        subscription.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
        subscription.start_date = None
        subscription.end_date = None
        if subscription.user.role not in {"admin", "reporter"}:
            subscription.user.role = "free_user"
    elif new_status == "active":
        subscription.plan_name = "paid"
        subscription.status = "active"
        subscription.start_date = now.date()
        subscription.end_date = None
        if subscription.user.role not in {"admin", "reporter"}:
            subscription.user.role = "paid_user"
    elif new_status == "free":
        subscription.plan_name = "free"
        subscription.status = "free"
        subscription.trial_started_at = None
        subscription.trial_ends_at = None
        subscription.start_date = None
        subscription.end_date = None
        if subscription.user.role not in {"admin", "reporter"}:
            subscription.user.role = "free_user"
    elif new_status == "expired":
        subscription.status = "expired"
        if subscription.user.role not in {"admin", "reporter"}:
            subscription.user.role = "free_user"
    elif new_status == "cancelled":
        subscription.status = "cancelled"
        if subscription.user.role not in {"admin", "reporter"}:
            subscription.user.role = "free_user"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid subscription status",
        )

    if commit:
        db.commit()
        db.refresh(subscription)
    else:
        db.flush()
    return subscription


PAID_PLAN_DURATIONS_DAYS = {"monthly": 30, "seasonal": 90}


def activate_paid_subscription(db: Session, subscription: Subscription, *, plan: str, now: datetime | None = None, commit: bool = True) -> Subscription:
    """Activate paid access for a completed payment. Distinct from
    update_subscription_status's "active" branch (used for manual admin grants,
    which stay indefinite/end_date=None) - a payment always has a real
    end_date matching what was actually paid for."""
    current_time = now or utc_now()
    duration_days = PAID_PLAN_DURATIONS_DAYS[plan]
    anchor_date = current_time.date()
    # Owner-approved carry-forward only for currently usable, dated access.
    # Ignore stale dates on free/expired/cancelled subscriptions. Manual-grant
    # payment handling is a separate business decision; no new rule here.
    if subscription.status == "active" and subscription.end_date is not None:
        anchor_date = max(anchor_date, subscription.end_date)
    elif subscription.status == "trial" and subscription.trial_ends_at is not None:
        trial_end = subscription.trial_ends_at
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if trial_end > current_time:
            anchor_date = max(anchor_date, trial_end.astimezone(timezone.utc).date())
    subscription.plan_name = f"paid_{plan}"
    subscription.status = "active"
    subscription.start_date = current_time.date()
    subscription.end_date = anchor_date + timedelta(days=duration_days)
    if subscription.user.role not in {"admin", "reporter"}:
        subscription.user.role = "paid_user"
    if commit:
        db.commit()
        db.refresh(subscription)
    else:
        db.flush()
    return subscription


REFERRAL_REWARD_DAYS = 7
REFERRAL_REWARD_LIMIT = 3
REFERRAL_REWARD_WINDOW_DAYS = 30


def apply_referral_reward(db: Session, referrer: User, *, commit: bool = True) -> bool:
    """Extend the referrer's trial when someone they referred registers. Only applies
    to trial/free accounts - active/expired/cancelled subscriptions are left untouched
    since extra "trial days" has no meaning for them."""
    db.scalar(select(User).where(User.id == referrer.id).with_for_update().execution_options(populate_existing=True))
    subscription = db.scalar(select(Subscription).where(Subscription.user_id == referrer.id).with_for_update().execution_options(populate_existing=True))
    if subscription is None:
        return False

    now = utc_now()
    trial_expired = apply_trial_expiry(subscription, now=now)
    paid_expired = apply_paid_expiry(subscription, now=now)
    if subscription.status in {"trial", "free"}:
        # The parent-account lock above serializes this check with registration's
        # atomic award/audit commit. Count known awards only; never rewrite days
        # or infer missing legacy evidence. The window uses elapsed UTC time.
        recent = db.scalar(select(func.count(AuditLog.id)).where(
            AuditLog.user_id == referrer.id, AuditLog.action == "referral.reward_granted",
            AuditLog.table_name == "subscriptions",
            AuditLog.created_at > now - timedelta(days=REFERRAL_REWARD_WINDOW_DAYS),
            AuditLog.created_at <= now,
        )) or 0
        if recent >= REFERRAL_REWARD_LIMIT:
            return False
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
        if commit and (trial_expired or paid_expired):
            db.commit()
            db.refresh(subscription)
        return False

    if commit:
        db.commit()
        db.refresh(subscription)
    else:
        db.flush()
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
