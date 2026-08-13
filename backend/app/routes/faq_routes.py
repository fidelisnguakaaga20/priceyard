from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faq_item import FAQItem
from app.models.user import User
from app.schemas.faq_schema import FAQAdminResponse, FAQCreate, FAQPublicResponse, FAQUpdate
from app.services.faq_service import (
    create_faq,
    delete_faq,
    get_faq_for_admin,
    get_published_faq,
    list_published_faqs,
    set_faq_publication,
    update_faq,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/faq", tags=["faq"])


@router.get("", response_model=list[FAQPublicResponse])
def get_published_items(db: Session = Depends(get_db)) -> list[FAQItem]:
    return list_published_faqs(db)


@router.get("/{faq_id}", response_model=FAQPublicResponse)
def get_published_item(faq_id: int, db: Session = Depends(get_db)) -> FAQItem:
    return get_published_faq(db, faq_id)


@router.post("", response_model=FAQAdminResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: FAQCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> FAQItem:
    return create_faq(db, payload, admin)


@router.patch("/{faq_id}", response_model=FAQAdminResponse)
def edit_item(
    faq_id: int,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> FAQItem:
    return update_faq(db, get_faq_for_admin(db, faq_id), payload)


@router.patch("/{faq_id}/publish", response_model=FAQAdminResponse)
def publish_item(
    faq_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> FAQItem:
    return set_faq_publication(db, get_faq_for_admin(db, faq_id), is_published=True)


@router.patch("/{faq_id}/hide", response_model=FAQAdminResponse)
def hide_item(
    faq_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> FAQItem:
    return set_faq_publication(db, get_faq_for_admin(db, faq_id), is_published=False)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    faq_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_faq(db, get_faq_for_admin(db, faq_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
