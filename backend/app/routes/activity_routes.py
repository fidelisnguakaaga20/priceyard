from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.rate_limit import limiter
from app.schemas.activity_schema import ActivityPingRequest, ActivitySummaryResponse
from app.services.activity_service import get_activity_summary, log_activity_event, mark_all_seen
from app.utils.permissions import require_roles

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/ping", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
def ping(request: Request, payload: ActivityPingRequest, db: Session = Depends(get_db)) -> None:
    """Public, unauthenticated: records that someone opened the app or a shared link.
    No visitor identity is captured - this is a count/feed for the admin, not tracking."""
    log_activity_event(db, event_type=payload.event_type, label=payload.label)


@router.get("/summary", response_model=ActivitySummaryResponse)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> ActivitySummaryResponse:
    return ActivitySummaryResponse(**get_activity_summary(db))


@router.post("/seen", status_code=status.HTTP_204_NO_CONTENT)
def seen(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> None:
    mark_all_seen(db)
