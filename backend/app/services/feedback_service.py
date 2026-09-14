from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback_schema import FeedbackCreate, FeedbackSummaryResponse, TestimonialResponse


def create_feedback(db: Session, current_user: User, payload: FeedbackCreate) -> Feedback:
    item = Feedback(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_feedback(db: Session, rating: int | None = None) -> list[Feedback]:
    statement = select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc())
    if rating is not None:
        statement = statement.where(Feedback.rating == rating)
    return list(db.scalars(statement).all())


def get_feedback(db: Session, feedback_id: int) -> Feedback:
    item = db.get(Feedback, feedback_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return item


def feedback_summary(db: Session) -> FeedbackSummaryResponse:
    count_value, average_value = db.execute(
        select(func.count(Feedback.id), func.avg(Feedback.rating))
    ).one()
    return FeedbackSummaryResponse(
        count=int(count_value or 0),
        average_rating=float(average_value) if average_value is not None else None,
    )


def delete_feedback(db: Session, item: Feedback) -> None:
    db.delete(item)
    db.commit()


def _testimonial_quote(item: Feedback) -> str | None:
    return item.complaint_or_suggestion or item.comment


def set_testimonial_publication(db: Session, item: Feedback, *, is_public: bool, display_name: str | None) -> Feedback:
    if is_public and not _testimonial_quote(item):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This feedback has no text to display as a testimonial")
    item.is_public_testimonial = is_public
    item.testimonial_display_name = display_name if is_public else item.testimonial_display_name
    db.commit()
    db.refresh(item)
    return item


def list_public_testimonials(db: Session) -> list[TestimonialResponse]:
    statement = (
        select(Feedback)
        .where(Feedback.is_public_testimonial.is_(True))
        .order_by(Feedback.created_at.desc())
    )
    items = db.scalars(statement).all()
    return [
        TestimonialResponse(
            id=item.id,
            rating=item.rating,
            quote=_testimonial_quote(item) or "",
            display_name=item.testimonial_display_name or "PriceYard user",
            created_at=item.created_at,
        )
        for item in items
    ]
