from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_metrics_schema import AdminMetricsResponse
from app.services.admin_metrics_service import get_admin_metrics
from app.utils.permissions import require_roles

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/metrics", response_model=AdminMetricsResponse)
def metrics(
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AdminMetricsResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return get_admin_metrics(db)
