from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.price_update import PriceUpdate
from app.models.user import User
from app.models.watchlist import Watchlist


def _notification_prices_url(settings) -> str:
    """Validate an explicit application origin without DNS or a live fallback."""
    value = getattr(settings, "frontend_url", None)
    environment = getattr(settings, "app_env", None)
    # Settings has a development default; it must not silently become a mailed
    # destination when FRONTEND_URL was omitted from environment configuration.
    explicit = getattr(settings, "model_fields_set", {"frontend_url"})
    if ("frontend_url" not in explicit or not isinstance(value, str) or not value or len(value) > 2048
            or environment not in {"production", "staging", "development", "test"}
            or any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value)
            or any(character in value for character in ("\\", "%", "?", "#"))):
        raise ValueError("Notification application URL is not configured safely")
    try:
        parsed = urlsplit(value)
        host, port = parsed.hostname, parsed.port
        if (not host or len(host) > 253 or parsed.username is not None or parsed.password is not None
                or parsed.path not in {"", "/"} or port == 0):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
            if host != "localhost" and (len(host.split('.')) < 2
                    or not any(character.isalpha() for character in host.split('.')[-1])
                    or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                           for label in host.split('.'))):
                raise ValueError
        loopback = host == "localhost" or address is not None and address.is_loopback
        local_test = environment in {"development", "test"} and loopback
        if parsed.scheme != "https" and not (parsed.scheme == "http" and local_test):
            raise ValueError
        if (loopback or address is not None and not address.is_global) and not local_test:
            raise ValueError
        # This is a deny rule for the original known live host, never a URL
        # fallback. Additional live domains must be reviewed before staging use.
        if environment != "production" and (host == "priceyard.onrender.com" or host.endswith(".priceyard.onrender.com")):
            raise ValueError
    except ValueError:
        raise ValueError("Notification application URL is not configured safely") from None
    return urlunsplit((parsed.scheme, parsed.netloc, "/prices", "", ""))


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
    from app.services.whatsapp_service import send_whatsapp_message

    try:
        prices_url = _notification_prices_url(get_settings())
    except ValueError:
        # A configuration fault must not send an unsafe link or undo a saved
        # price approval. No watcher query or provider call has occurred yet.
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
            f"Check it here: {prices_url}\n\n"
            "You are getting this because you saved this commodity or market to "
            "your watchlist. Manage your watchlist anytime from your Dashboard.\n\n"
            "PriceYard - Know the market before you buy or sell."
        )
        try:
            send_email(recipient=user.email, subject=subject, body=body)
            sent += 1
        except Exception:
            # A failed email must not suppress this user's other channels.
            pass

        try:
            send_push_to_user(
                db,
                user.id,
                title=f"{price_update.commodity.name} price update",
                body=f"{price_update.market.name}: {price_update.price_low:,.0f}–{price_update.price_high:,.0f} {price_update.unit}",
                url=prices_url,
            )
        except Exception:
            pass

        if user.phone:
            try:
                send_whatsapp_message(
                    to_phone=user.phone,
                    body=(
                        f"PriceYard: {price_update.commodity.name} at {price_update.market.name} is now "
                        f"NGN {price_update.price_low:,.0f} - NGN {price_update.price_high:,.0f} ({price_update.unit}). "
                        f"{prices_url}"
                    ),
                )
            except Exception:
                continue
    return sent
