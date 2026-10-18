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
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.services.feedback_service import (
    create_feedback,
    delete_feedback,
    feedback_summary,
    get_feedback,
    list_public_testimonials,
    set_testimonial_publication,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/feedback", tags=["feedback"])
testimonials_router = APIRouter(prefix="/testimonials", tags=["testimonials"])


def _feedback_snapshot(item: Feedback) -> dict:
    # Keep the original private attachment on Feedback, not duplicated in logs.
    return snapshot_model(item, extra_exclude={"screenshot_data"})


def _save_feedback_audit(db: Session, admin: User, action: str, record_id: int, *, old_value: dict, new_value: dict | None = None) -> None:
    try:
        create_audit_log(db, actor=admin, action=action, table_name="feedback", record_id=record_id,
                         old_value=old_value, new_value=new_value, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise


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
) -> Response:
    conditions = (Feedback.rating == rating,) if rating is not None else ()
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Feedback, FeedbackResponse,
        order=(("created_at", True), ("id", True)), where=conditions))


@router.get("/admin/page", response_model=AdminRecordPage[FeedbackResponse])
def get_feedback_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    rating: int | None = Query(default=None, ge=1, le=5),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles("admin")),
) -> AdminRecordPage[FeedbackResponse]:
    conditions = (Feedback.rating == rating,) if rating is not None else ()
    return admin_record_page(db, Feedback, FeedbackResponse, offset=offset,
        order=(("created_at", True), ("id", True)), where=conditions)


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
    item = get_feedback(db, feedback_id, lock=True)
    old_value = _feedback_snapshot(item)
    item = set_testimonial_publication(db, item, is_public=True, display_name=payload.display_name, commit=False)
    _save_feedback_audit(db, admin, "feedback.testimonial_publish", item.id, old_value=old_value, new_value=_feedback_snapshot(item))
    return item


@router.patch("/{feedback_id}/testimonial/hide", response_model=FeedbackResponse)
def hide_testimonial(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Feedback:
    item = get_feedback(db, feedback_id, lock=True)
    old_value = _feedback_snapshot(item)
    item = set_testimonial_publication(db, item, is_public=False, display_name=item.testimonial_display_name, commit=False)
    _save_feedback_audit(db, admin, "feedback.testimonial_hide", item.id, old_value=old_value, new_value=_feedback_snapshot(item))
    return item


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_feedback(db, feedback_id, lock=True)
    old_value = _feedback_snapshot(item)
    record_id = item.id
    delete_feedback(db, item, commit=False)
    _save_feedback_audit(db, admin, "feedback.delete", record_id, old_value=old_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
