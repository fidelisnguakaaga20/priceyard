from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_summary_schema import AdminSummary
from app.services.admin_summary_service import get_admin_summary
from app.utils.permissions import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/summary", response_model=AdminSummary)
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))) -> AdminSummary:
    return get_admin_summary(db)
