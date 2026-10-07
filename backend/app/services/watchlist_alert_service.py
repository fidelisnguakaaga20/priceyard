from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist


def _target_condition_met(item: Watchlist, price_update: PriceUpdate) -> bool:
    """No target set means the legacy "any change" behavior -- always notify. A target
    compares against whichever end of the price range is relevant to that direction:
    a buyer watching for a dip cares whether the range's low reaches their target,
    a seller watching for a rise cares whether the range's high does."""
    if item.target_price is None:
        return True
    if item.target_direction == "at_or_below":
        return price_update.price_low <= item.target_price
    if item.target_direction == "at_or_above":
        return price_update.price_high >= item.target_price
    return True


def notify_watchlist_subscribers(db: Session, price_update: PriceUpdate) -> int:
    """Email and push-notify users whose watchlist matches this newly-approved price
    update's commodity and/or market, and whose target price (if any) was just met.
    Best-effort only - a failed send for one user must never block approval or affect
    other users."""
    from app.config import get_settings
    from app.services.email_service import send_email
    from app.services.push_service import send_push_to_user

    frontend_url = get_settings().frontend_url.rstrip("/")

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
    qualifying_users: dict[int, User] = {}
    for item in watchers:
        user = item.user
        if user is None or not user.is_active or user.id in qualifying_users:
            continue
        if _target_condition_met(item, price_update):
            qualifying_users[user.id] = user

    sent = 0
    for user in qualifying_users.values():
        subject = f"{price_update.commodity.name} price update on PriceYard"
        body = (
            f"Hi {user.full_name},\n\n"
            f"A price update was just published for {price_update.commodity.name} "
            f"at {price_update.market.name}:\n"
            f"NGN {price_update.price_low:,.0f} - NGN {price_update.price_high:,.0f} "
            f"({price_update.unit})\n\n"
            "Check it here: https://priceyard.onrender.com/prices\n\n"
            "You are getting this because you saved this commodity or market to "
            "your watchlist. Manage your watchlist anytime from your Dashboard.\n\n"
            "PriceYard - Know the market before you buy or sell."
        )
        try:
            send_email(recipient=user.email, subject=subject, body=body)
            sent += 1
        except Exception:
            continue

        try:
            send_push_to_user(
                db,
                user.id,
                title=f"{price_update.commodity.name} price update",
                body=f"{price_update.market.name}: {price_update.price_low:,.0f}–{price_update.price_high:,.0f} {price_update.unit}",
                url=f"{frontend_url}/prices",
            )
        except Exception:
            continue
    return sent
