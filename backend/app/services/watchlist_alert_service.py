from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.push_subscription import PushSubscription
from app.utils.price_measurement import normalize_label


def current_public_observation(db: Session, price_update: PriceUpdate) -> bool:
    """Queued summaries must still describe the current approved observation."""
    statement = select(PriceUpdate.id).join(Commodity).join(Market).where(
        PriceUpdate.commodity_id == price_update.commodity_id,
        PriceUpdate.market_id == price_update.market_id,
        PriceUpdate.status == "approved", Commodity.is_active.is_(True), Market.is_active.is_(True),
    )
    for field in ("unit", "bag_size", "commodity_type", "grade"):
        statement = statement.where(func.lower(func.trim(func.coalesce(getattr(PriceUpdate, field), ""))) == normalize_label(getattr(price_update, field)))
    latest = db.scalar(statement.order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc()).limit(1))
    visible = db.scalar(select(PriceUpdate.id).where(PriceUpdate.id == price_update.id, PriceUpdate.is_outdated.is_(False)))
    return latest == price_update.id and visible is not None


def watch_matches(item: Watchlist, price_update: PriceUpdate) -> bool:
    return (
        (item.commodity_id is None or item.commodity_id == price_update.commodity_id)
        and (item.market_id is None or item.market_id == price_update.market_id)
    )


def _target_condition_met(item: Watchlist, price_update: PriceUpdate) -> bool:
    """No target set means the legacy "any change" behavior -- always notify. A target
    compares against whichever end of the price range is relevant to that direction:
    a buyer watching for a dip cares whether the range's low reaches their target,
    a seller watching for a rise cares whether the range's high does."""
    if item.target_price is None:
        return True
    if not item.target_measurement_confirmed:
        return False
    for target_field, price_field in (("target_unit", "unit"), ("target_bag_size", "bag_size"),
                                    ("target_commodity_type", "commodity_type"), ("target_grade", "grade")):
        if normalize_label(getattr(item, target_field)) != normalize_label(getattr(price_update, price_field)):
            return False
    if item.target_direction == "at_or_below":
        return price_update.price_low <= item.target_price
    if item.target_direction == "at_or_above":
        return price_update.price_high >= item.target_price
    return False


def notify_watchlist_subscribers(db: Session, price_update: PriceUpdate) -> int:
    """Queue public price facts only; providers never run in the approval request."""
    from app.config import get_settings
    from app.services.notification_service import enqueue_notification

    frontend_url = get_settings().frontend_url.rstrip("/")
    if not current_public_observation(db, price_update):
        return 0

    statement = (
        select(Watchlist)
        .where(
            or_(
                Watchlist.commodity_id == price_update.commodity_id,
                Watchlist.market_id == price_update.market_id,
            )
        )
        .options(selectinload(Watchlist.user))
    )
    watchers = db.scalars(statement).all()

    # A user can have more than one matching watchlist row (e.g. the commodity and the
    # market separately) -- they qualify if ANY of those rows has no target, or has a
    # target that this update just met.
    qualifying_users: dict[int, tuple[User, list[int]]] = {}
    for item in watchers:
        user = item.user
        if user is None or not user.is_active:
            continue
        # A combined watch means this commodity in this market, not either one.
        if item.commodity_id is not None and item.commodity_id != price_update.commodity_id:
            continue
        if item.market_id is not None and item.market_id != price_update.market_id:
            continue
        if watch_matches(item, price_update) and _target_condition_met(item, price_update):
            if user.id not in qualifying_users:
                qualifying_users[user.id] = (user, [])
            qualifying_users[user.id][1].append(item.id)

    sent = 0
    subscribed_users = set(db.scalars(select(PushSubscription.user_id).where(PushSubscription.user_id.in_(qualifying_users))).all()) if qualifying_users else set()
    measurement = " / ".join(value for value in (price_update.unit, price_update.bag_size or "unspecified package", price_update.commodity_type, price_update.grade) if value)
    from app.services.auth_session_service import utc_aware
    from app.utils.price_measurement import LAGOS_TIMEZONE
    observed = utc_aware(price_update.update_date_time).astimezone(LAGOS_TIMEZONE).strftime("%d %b %Y, %H:%M WAT")
    for user, watch_ids in qualifying_users.values():
        subject = f"{price_update.commodity.name} price update on PriceYard"
        body = (
            f"Hi {user.full_name},\n\n"
            f"A price update was just published for {price_update.commodity.name} "
            f"at {price_update.market.name}:\n"
            f"NGN {price_update.price_low:,.0f} - NGN {price_update.price_high:,.0f} "
            f"({measurement})\nObserved: {observed}\n\n"
            f"Check it here: {frontend_url}/prices\n\n"
            "You are getting this because you saved this commodity or market to "
            "your watchlist. Manage your watchlist anytime from your Dashboard.\n\n"
            "PriceYard - Know the market before you buy or sell."
        )
        event_key = f"price:{price_update.id}:{price_update.updated_at.isoformat()}:{user.id}"
        metadata = {"_user_id": user.id, "_price_update_id": price_update.id,
                    "_watchlist_ids": watch_ids, "_price_revision": utc_aware(price_update.updated_at).isoformat()}
        if enqueue_notification(db, channel="email", recipient=user.email,
                                payload={"subject": subject, "body": body, **metadata}, event_key=event_key):
            sent += 1
        if user.id in subscribed_users:
            enqueue_notification(db, channel="push", recipient=str(user.id), payload={
                "title": f"{price_update.commodity.name} price update",
                "body": f"{price_update.market.name}: NGN {price_update.price_low:,.0f} - {price_update.price_high:,.0f} ({measurement})",
                "url": f"{frontend_url}/prices", **metadata,
            }, event_key=event_key)
        if user.phone:
            enqueue_notification(db, channel="whatsapp", recipient=user.phone,
                                 payload={"body": f"{subject}: NGN {price_update.price_low:,.0f} - {price_update.price_high:,.0f} ({measurement}). Observed {observed}. {frontend_url}/prices", **metadata},
                                 event_key=event_key)
    return sent
