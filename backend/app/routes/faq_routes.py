from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faq_item import FAQItem
from app.models.user import User
from app.schemas.faq_schema import FAQAdminResponse, FAQCreate, FAQPublicResponse, FAQUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.faq_service import (
    create_faq,
    delete_faq,
    get_faq_for_admin,
    get_published_faq,
    list_published_faqs,
    list_admin_faqs,
    set_faq_publication,
    update_faq,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/faq", tags=["faq"])


def _save_faq_audit(db: Session, admin: User, action: str, record_id: int, *, old_value: dict | None = None, new_value: dict | None = None) -> None:
    try:
        create_audit_log(db, actor=admin, action=action, table_name="faq_items", record_id=record_id,
                         old_value=old_value, new_value=new_value, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[FAQPublicResponse])
def get_published_items(db: Session = Depends(get_db)) -> list[FAQItem]:
    return list_published_faqs(db)


@router.get("/admin", response_model=list[FAQAdminResponse])
def get_admin_items(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[FAQItem]:
    return list_admin_faqs(db)


@router.get("/{faq_id}", response_model=FAQPublicResponse)
def get_published_item(faq_id: int, db: Session = Depends(get_db)) -> FAQItem:
    return get_published_faq(db, faq_id)


@router.post("", response_model=FAQAdminResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: FAQCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> FAQItem:
    item = create_faq(db, payload, admin, commit=False)
    _save_faq_audit(db, admin, "faq.create", item.id, new_value=snapshot_model(item))
    return item


@router.patch("/{faq_id}", response_model=FAQAdminResponse)
def edit_item(
    faq_id: int,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> FAQItem:
    item = get_faq_for_admin(db, faq_id, lock=True)
    old_value = snapshot_model(item)
    item = update_faq(db, item, payload, commit=False)
    _save_faq_audit(db, admin, "faq.edit", item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.patch("/{faq_id}/publish", response_model=FAQAdminResponse)
def publish_item(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> FAQItem:
    item = get_faq_for_admin(db, faq_id, lock=True)
    old_value = snapshot_model(item)
    item = set_faq_publication(db, item, is_published=True, commit=False)
    _save_faq_audit(db, admin, "faq.publish", item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.patch("/{faq_id}/hide", response_model=FAQAdminResponse)
def hide_item(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> FAQItem:
    item = get_faq_for_admin(db, faq_id, lock=True)
    old_value = snapshot_model(item)
    item = set_faq_publication(db, item, is_published=False, commit=False)
    _save_faq_audit(db, admin, "faq.hide", item.id, old_value=old_value, new_value=snapshot_model(item))
    return item


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Response:
    item = get_faq_for_admin(db, faq_id, lock=True)
    old_value = snapshot_model(item)
    record_id = item.id
    delete_faq(db, item, commit=False)
    _save_faq_audit(db, admin, "faq.delete", record_id, old_value=old_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
