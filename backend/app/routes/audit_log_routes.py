from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log_schema import AuditLogResponse
from app.services.audit_service import get_audit_log
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.utils.permissions import require_roles

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogResponse])
def get_logs(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    return AdminJSONResponse(stream_admin_records(db.get_bind(), AuditLog, AuditLogResponse,
        order=(("created_at", True), ("id", True))))


@router.get("/page", response_model=AdminRecordPage[AuditLogResponse])
def get_logs_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AdminRecordPage[AuditLogResponse]:
    return admin_record_page(db, AuditLog, AuditLogResponse, offset=offset,
        order=(("created_at", True), ("id", True)))


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AuditLog:
    return get_audit_log(db, audit_log_id)
