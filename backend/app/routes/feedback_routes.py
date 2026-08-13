from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback_schema import FeedbackCreate, FeedbackResponse, FeedbackSummaryResponse
from app.services.feedback_service import (
    create_feedback,
    delete_feedback,
    feedback_summary,
    get_feedback,
    list_feedback,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Feedback:
    return create_feedback(db, current_user, payload)


@router.get("/summary", response_model=FeedbackSummaryResponse)
def get_feedback_summary(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> FeedbackSummaryResponse:
    return feedback_summary(db)


@router.get("", response_model=list[FeedbackResponse])
def get_feedback_list(
    rating: int | None = Query(default=None, ge=1, le=5),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> list[Feedback]:
    return list_feedback(db, rating=rating)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback_item(
    feedback_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Feedback:
    return get_feedback(db, feedback_id)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_feedback(db, feedback_id)
    delete_feedback(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
