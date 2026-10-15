from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log_schema import AuditLogResponse
from app.services.audit_service import get_audit_log, list_audit_logs
from app.utils.permissions import require_roles

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogResponse])
def get_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[AuditLog]:
    return list_audit_logs(db, page=page, page_size=page_size)


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AuditLog:
    return get_audit_log(db, audit_log_id)
