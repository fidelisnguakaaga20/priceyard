from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.price_update import PriceUpdate
from app.models.watchlist import Watchlist


def notify_watchlist_subscribers(db: Session, price_update: PriceUpdate) -> int:
    """Email and push-notify users whose watchlist matches this newly-approved price
    update's commodity and/or market. Best-effort only - a failed send for one user
    must never block approval or affect other users."""
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

    seen_user_ids: set[int] = set()
    sent = 0
    for item in watchers:
        user = item.user
        if user is None or user.id in seen_user_ids or not user.is_active:
            continue
        seen_user_ids.add(user.id)

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
