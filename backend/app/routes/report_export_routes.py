from datetime import date

import anyio
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse

from app.database import get_db
from app.models.user import User
from app.services.report_export_service import stream_price_report_csv
from app.utils.permissions import require_roles

router = APIRouter(prefix="/reports", tags=["reports"])


class _PriceReportResponse(StreamingResponse):
    def __init__(self, content, **kwargs):
        self._report_content = content
        super().__init__(content, **kwargs)

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            # Close the cursor/session after success, client disconnect or a
            # failed send, including cancellation of the streaming task.
            with anyio.CancelScope(shield=True):
                await run_in_threadpool(self._report_content.close)


@router.get("/prices.csv")
def export_price_report_csv(
    commodity: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_roles("admin")),
) -> Response:
    content = stream_price_report_csv(
        db.get_bind(),
        commodity_search=commodity,
        market_search=market,
        date_from=date_from,
        date_to=date_to,
    )
    return _PriceReportResponse(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="priceyard-price-report.csv"'},
    )
