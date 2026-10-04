from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent

VALID_EVENT_TYPES = frozenset({"app_visit", "share_view"})
RECENT_LIMIT = 50


def log_activity_event(db: Session, *, event_type: str, label: str | None = None) -> ActivityEvent:
    if event_type not in VALID_EVENT_TYPES:
        event_type = "app_visit"
    item = ActivityEvent(event_type=event_type, label=label[:200] if label else None)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_activity_summary(db: Session) -> dict:
    unseen_count = db.scalar(select(func.count()).select_from(ActivityEvent).where(ActivityEvent.seen.is_(False))) or 0
    recent = list(
        db.scalars(select(ActivityEvent).order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc()).limit(RECENT_LIMIT)).all()
    )
    return {"unseen_count": unseen_count, "recent": recent}


def mark_all_seen(db: Session) -> None:
    db.execute(update(ActivityEvent).where(ActivityEvent.seen.is_(False)).values(seen=True))
    db.commit()
