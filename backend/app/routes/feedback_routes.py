from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback_schema import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackSummaryResponse,
    TestimonialPublishRequest,
    TestimonialResponse,
)
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.feedback_service import (
    create_feedback,
    delete_feedback,
    feedback_summary,
    get_feedback,
    list_feedback,
    list_public_testimonials,
    set_testimonial_publication,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/feedback", tags=["feedback"])
testimonials_router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@testimonials_router.get("", response_model=list[TestimonialResponse])
def get_public_testimonials(db: Session = Depends(get_db)) -> list[TestimonialResponse]:
    return list_public_testimonials(db)


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


@router.patch("/{feedback_id}/testimonial/publish", response_model=FeedbackResponse)
def publish_testimonial(
    feedback_id: int,
    payload: TestimonialPublishRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Feedback:
    item = get_feedback(db, feedback_id)
    old_value = snapshot_model(item)
    item = set_testimonial_publication(db, item, is_public=True, display_name=payload.display_name)
    create_audit_log(db, actor=admin, action="feedback.testimonial_publish", table_name="feedback", record_id=item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.patch("/{feedback_id}/testimonial/hide", response_model=FeedbackResponse)
def hide_testimonial(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Feedback:
    item = get_feedback(db, feedback_id)
    old_value = snapshot_model(item)
    item = set_testimonial_publication(db, item, is_public=False, display_name=item.testimonial_display_name)
    create_audit_log(db, actor=admin, action="feedback.testimonial_hide", table_name="feedback", record_id=item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_feedback(db, feedback_id)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_feedback(db, item)
    create_audit_log(db, actor=admin, action="feedback.delete", table_name="feedback", record_id=record_id, old_value=old_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
