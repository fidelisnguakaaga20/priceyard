from datetime import datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.referral_reward import ReferralReward
from app.models.user import User

TRIAL_DURATION_DAYS = 14
PAID_PLAN_DURATIONS_DAYS = {"monthly": 30, "seasonal": 90}
REFERRAL_REWARD_DAYS = 7
# Prospective qualifying-purchase awards only. Previously earned trial days stay intact.
REFERRAL_REWARD_CAP = 4

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def aware_utc(value: datetime) -> datetime:
    # Legacy naive database timestamps are UTC; new API timestamps require offsets.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def paid_cutoff(subscription: Subscription) -> datetime | None:
    if subscription.paid_expires_at is not None:
        return aware_utc(subscription.paid_expires_at)
    if subscription.end_date is not None:
        # Legacy expiry included the whole UTC end_date. Do not remove that day.
        return datetime.combine(subscription.end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return None


def is_manual_grant(subscription: Subscription) -> bool:
    return bool(subscription.manual_grant) or (
        subscription.status == "active" and subscription.end_date is None and subscription.paid_expires_at is None
    )


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

    current_time = aware_utc(now or utc_now())
    trial_end = subscription.trial_ends_at
    if trial_end.tzinfo is None:
        trial_end = trial_end.replace(tzinfo=timezone.utc)

    if current_time < trial_end:
        return False

    subscription.status = "expired"
    return True


def apply_paid_expiry(subscription: Subscription, *, now: datetime | None = None) -> bool:
    """Expire a paid subscription once its end_date passes. A manually-activated
    (admin) subscription has end_date=None and never expires this way - only
    payment-driven activations (which set a real end_date) are affected."""
    if subscription.status not in ("active", "cancelled") or is_manual_grant(subscription):
        return False
    cutoff = paid_cutoff(subscription)
    if cutoff is None or aware_utc(now or utc_now()) < cutoff:
        return False

    subscription.status = "expired"
    return True


def expire_trial_if_needed(db: Session, subscription: Subscription, *, now: datetime | None = None) -> Subscription:
    trial_changed = apply_trial_expiry(subscription, now=now)
    paid_changed = apply_paid_expiry(subscription, now=now)
    if trial_changed or paid_changed:
        db.flush()
    return subscription


def has_full_access(subscription: Subscription, *, now: datetime | None = None) -> bool:
    if subscription.status in ("active", "cancelled"):
        if is_manual_grant(subscription):
            return True
        cutoff = paid_cutoff(subscription)
        return cutoff is not None and aware_utc(now or utc_now()) < cutoff
    if subscription.status != "trial" or subscription.trial_ends_at is None:
        return False

    current_time = aware_utc(now or utc_now())
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


def list_subscriptions(db: Session, *, page: int = 1, page_size: int = 100) -> list[Subscription]:
    if page < 1 or not 1 <= page_size <= 1000:
        raise HTTPException(status_code=422, detail="Invalid pagination")
    now = aware_utc(utc_now())
    # Apply time-derived status to ALL expired rows, not just the displayed page.
    # These bounded SQL statements do not materialize an ever-growing account list
    # and never modify operational roles or overwrite future/manual entitlements.
    db.execute(update(Subscription).where(Subscription.status == "trial", Subscription.trial_ends_at <= now)
               .values(status="expired").execution_options(synchronize_session="fetch"))
    db.execute(update(Subscription).where(
        Subscription.status.in_(("active", "cancelled")), Subscription.manual_grant.is_(False),
        or_(Subscription.paid_expires_at <= now,
            and_(Subscription.paid_expires_at.is_(None), Subscription.end_date < now.date())),
    ).values(status="expired").execution_options(synchronize_session="fetch"))
    return list(db.scalars(select(Subscription).order_by(Subscription.id)
                          .offset((page - 1) * page_size).limit(page_size)).all())


def update_subscription_status(db: Session, subscription: Subscription, new_status: str) -> Subscription:
    now = utc_now()

    # Commercial status changes must never shorten valid purchased/manual access.
    protected = is_manual_grant(subscription) or (
        paid_cutoff(subscription) is not None and paid_cutoff(subscription) > now
    )
    if protected and new_status in ("trial", "free", "expired"):
        raise HTTPException(status_code=409, detail="Valid purchased or manual access cannot be overwritten; use an audited adjustment process")

    if new_status == "trial":
        subscription.plan_name = "trial"
        subscription.status = "trial"
        subscription.trial_started_at = now
        subscription.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
        subscription.trial_reminder_sent_at = None
        subscription.start_date = None
        subscription.end_date = None
        subscription.paid_expires_at = None
        subscription.manual_grant = False
    elif new_status == "active":
        subscription.plan_name = "paid"
        subscription.status = "active"
        subscription.start_date = now.date()
        # Preserve any existing finite purchased cutoff in the ledger/projection.
        subscription.manual_grant = True
        if subscription.paid_expires_at is None and subscription.end_date is None:
            subscription.end_date = None
    elif new_status == "free":
        subscription.plan_name = "free"
        subscription.status = "free"
        subscription.trial_started_at = None
        subscription.trial_ends_at = None
        subscription.start_date = None
        subscription.end_date = None
        subscription.paid_expires_at = None
        subscription.manual_grant = False
    elif new_status == "expired":
        subscription.status = "expired"
    elif new_status == "cancelled":
        subscription.cancellation_requested_at = now
        # There are no recurring charges. Cancellation records intent without
        # deleting purchased time or a manual grant.
        if not protected:
            subscription.status = "cancelled"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid subscription status",
        )

    db.flush()
    return subscription


def activate_paid_subscription(db: Session, subscription: Subscription, *, plan: str, now: datetime | None = None, duration_days: int | None = None) -> Subscription:
    """Activate paid access for a completed payment. Distinct from
    update_subscription_status's "active" branch (used for manual admin grants,
    which stay indefinite/end_date=None) - a payment always has a real
    end_date matching what was actually paid for."""
    current_time = aware_utc(now or utc_now())
    if plan not in PAID_PLAN_DURATIONS_DAYS:
        raise HTTPException(status_code=422, detail="Invalid subscription plan")
    duration_days = duration_days or PAID_PLAN_DURATIONS_DAYS[plan]
    if duration_days <= 0:
        raise HTTPException(status_code=422, detail="Invalid purchased duration")
    if is_manual_grant(subscription):
        # A payment that predates a manual grant must not replace indefinite access.
        return subscription
    bases = [current_time]
    existing_cutoff = paid_cutoff(subscription)
    if existing_cutoff is not None:
        bases.append(existing_cutoff)
    if subscription.status == "trial" and subscription.trial_ends_at is not None:
        bases.append(aware_utc(subscription.trial_ends_at))
    expiry = max(bases) + timedelta(days=duration_days)
    subscription.plan_name = f"paid_{plan}"
    subscription.status = "active"
    subscription.start_date = subscription.start_date or current_time.date()
    subscription.paid_expires_at = expiry
    # Date compatibility for old clients: the day containing the last instant.
    subscription.end_date = (expiry - timedelta(microseconds=1)).date()
    subscription.cancellation_requested_at = None
    db.flush()
    return subscription


def apply_referral_reward(db: Session, referrer: User) -> bool:
    """Internal reward application, only invoked by qualified purchase processing.
    Extend trial/free access. Only applies
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

    subscription.trial_reminder_sent_at = None
    db.flush()
    return True


def qualify_referral_reward(db: Session, payment: Payment) -> bool:
    referred = payment.user
    referrer_id = referred.referred_by_id
    if referred.email_verified is not True or not referrer_id or referrer_id == referred.id:
        return False
    if db.scalar(select(ReferralReward.id).where(ReferralReward.referred_user_id == referred.id)) is not None:
        return False
    # Existing successful payments count: this campaign must not retroactively
    # qualify a second purchase as a customer's first successful purchase.
    previous = db.scalar(select(Payment.id).where(
        Payment.user_id == referred.id, Payment.id != payment.id, Payment.status == "success"
    ).limit(1))
    if previous is not None:
        return False
    referrer = db.scalar(select(User).where(User.id == referrer_id).with_for_update())
    if referrer is None or not referrer.is_active:
        return False
    awarded = db.scalar(select(func.count(ReferralReward.id)).where(ReferralReward.referrer_user_id == referrer_id)) or 0
    if awarded >= REFERRAL_REWARD_CAP:
        return False
    if not apply_referral_reward(db, referrer):
        return False
    db.add(ReferralReward(
        referred_user_id=referred.id, referrer_user_id=referrer.id,
        qualifying_payment_id=payment.id, reward_days=REFERRAL_REWARD_DAYS,
    ))
    db.flush()
    return True


TRIAL_REMINDER_WINDOW_DAYS = 3


def send_trial_expiry_reminders(db: Session) -> int:
    """Queue up to 200 reminders; the legacy sent_at field records enqueue time.

    Delivery is retried independently and rechecks the current trial/payment
    state. No provider is called before the request transaction commits.
    """
    from app.services.notification_service import enqueue_notification
    from app.utils.price_measurement import LAGOS_TIMEZONE
    from sqlalchemy.orm import selectinload

    settings = get_settings()
    dashboard_url = f"{settings.frontend_url.rstrip('/')}/dashboard"
    now = utc_now()
    window_end = now + timedelta(days=TRIAL_REMINDER_WINDOW_DAYS)
    candidates = db.scalars(
        select(Subscription).join(User).where(
            Subscription.status == "trial",
            Subscription.trial_ends_at.is_not(None),
            Subscription.trial_ends_at <= window_end,
            Subscription.trial_ends_at > now,
            Subscription.trial_reminder_sent_at.is_(None),
            User.is_active.is_(True),
        ).options(selectinload(Subscription.user)).order_by(Subscription.id)
        .with_for_update(skip_locked=True, of=Subscription).limit(200)
    ).all()

    sent = 0
    for subscription in candidates:
        user = subscription.user
        if not user.is_active:
            continue
        trial_end = aware_utc(subscription.trial_ends_at)
        end_display = trial_end.astimezone(LAGOS_TIMEZONE).strftime("%d %b %Y at %H:%M WAT")
        subject = "Your PriceYard trial ends soon"
        body = (
            f"Hi {user.full_name},\n\n"
            f"Your PriceYard trial ends on {end_display}. After it ends, "
            "you'll lose access to price history, buying zones, sell-watch windows, "
            "and storage suitability -- back to limited free access only.\n\n"
            "To keep full access, upgrade now from your dashboard:\n"
            f"{dashboard_url}\n\n"
            "Plans: NGN 2,500 for 30 days, or NGN 6,000 for 90 days.\n\n"
            "PriceYard — Know the market before you buy or sell."
        )
        enqueued = enqueue_notification(
            db, channel="email", recipient=user.email,
            payload={"subject": subject, "body": body, "_user_id": user.id, "_expires_at": trial_end.isoformat(),
                     "_trial_subscription_id": subscription.id, "_trial_ends_at": trial_end.isoformat()},
            event_key=f"trial-reminder:{subscription.id}:{trial_end.isoformat()}",
        )
        subscription.trial_reminder_sent_at = now
        if enqueued:
            sent += 1

    if candidates:
        db.flush()
    return sent
