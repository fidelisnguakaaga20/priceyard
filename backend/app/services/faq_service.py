from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.faq_item import FAQItem
from app.models.user import User
from app.schemas.faq_schema import FAQCreate, FAQUpdate


def create_faq(db: Session, payload: FAQCreate, admin: User) -> FAQItem:
    item = FAQItem(**payload.model_dump(), created_by=admin.id, is_published=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_faq_for_admin(db: Session, faq_id: int) -> FAQItem:
    item = db.get(FAQItem, faq_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ item not found")
    return item


def get_published_faq(db: Session, faq_id: int) -> FAQItem:
    item = db.scalar(
        select(FAQItem).where(FAQItem.id == faq_id, FAQItem.is_published.is_(True))
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ item not found")
    return item


def list_published_faqs(db: Session) -> list[FAQItem]:
    return list(
        db.scalars(
            select(FAQItem)
            .where(FAQItem.is_published.is_(True))
            .order_by(FAQItem.category.asc(), FAQItem.id.asc())
        ).all()
    )


def update_faq(db: Session, item: FAQItem, payload: FAQUpdate) -> FAQItem:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def set_faq_publication(db: Session, item: FAQItem, *, is_published: bool) -> FAQItem:
    item.is_published = is_published
    db.commit()
    db.refresh(item)
    return item


def delete_faq(db: Session, item: FAQItem) -> None:
    db.delete(item)
    db.commit()
