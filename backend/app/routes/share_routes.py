import json
from datetime import datetime, timezone
from html import escape as html_escape
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services.price_update_service import list_latest_approved_price_updates

router = APIRouter(prefix="/share", tags=["share"])


def _format_naira(value: object) -> str:
    return f"₦{float(value):,.0f}"


def _relative_age(moment: datetime) -> str:
    now = datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    hours = int((now - moment).total_seconds() // 3600)
    if hours < 1:
        return "moments ago"
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


@router.get("/commodities/{commodity_name}", response_class=HTMLResponse)
def share_commodity_card(commodity_name: str, db: Session = Depends(get_db)) -> HTMLResponse:
    """Serve a crawler-friendly HTML card with per-commodity Open Graph tags, then hand
    real visitors off to the React app. Social crawlers (WhatsApp, Facebook, Twitter, ...)
    don't execute JavaScript, so the SPA's single static index.html can't vary its preview
    per commodity — this route exists purely to give each shared price link its own
    title/description/image before redirecting a human to the actual page."""
    settings = get_settings()
    frontend_url = settings.frontend_url.rstrip("/")
    target_url = f"{frontend_url}/commodities/{quote(commodity_name, safe='')}"
    fallback_image = f"{frontend_url}/icons/icon-512.png"

    items = list_latest_approved_price_updates(db, commodity_search=commodity_name)
    item = items[0] if items else None

    if item is not None:
        measure = item.bag_size or item.unit
        title = f"{item.commodity.name} — {_format_naira(item.price_low)}–{_format_naira(item.price_high)} | PriceYard"
        description = (
            f"{item.commodity.name} at {item.market.name}: "
            f"{_format_naira(item.price_low)}–{_format_naira(item.price_high)} per {measure}. "
            f"Updated {_relative_age(item.update_date_time)}."
        )
        image = item.commodity.image_url or fallback_image
    else:
        title = f"{commodity_name} — PriceYard"
        description = "See today's market prices, ranges and trends on PriceYard."
        image = fallback_image

    safe_title = html_escape(title)
    safe_description = html_escape(description)
    safe_image = html_escape(image, quote=True)
    safe_target = html_escape(target_url, quote=True)
    target_json = json.dumps(target_url)

    html_body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{safe_title}</title>
<meta name="description" content="{safe_description}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{safe_title}" />
<meta property="og:description" content="{safe_description}" />
<meta property="og:image" content="{safe_image}" />
<meta property="og:url" content="{safe_target}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{safe_title}" />
<meta name="twitter:description" content="{safe_description}" />
<meta name="twitter:image" content="{safe_image}" />
<meta http-equiv="refresh" content="0; url={safe_target}" />
</head>
<body>
<p>Redirecting to <a href="{safe_target}">PriceYard</a>&hellip;</p>
<script>window.location.replace({target_json});</script>
</body>
</html>"""
    return HTMLResponse(content=html_body)
