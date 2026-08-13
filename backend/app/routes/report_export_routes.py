from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.report_export_service import build_price_report_csv, list_exportable_price_updates
from app.utils.permissions import require_roles

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/prices.csv")
def export_price_report_csv(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_roles("admin")),
) -> Response:
    items = list_exportable_price_updates(
        db,
        commodity_search=commodity,
        market_search=market,
        date_from=date_from,
        date_to=date_to,
    )
    content = build_price_report_csv(items)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="priceyard-price-report.csv"'},
    )
