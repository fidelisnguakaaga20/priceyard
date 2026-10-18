from __future__ import annotations

from sqlalchemy import func, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.price_flag import PriceFlag
from app.models.price_update import PriceUpdate
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.user import User
from app.schemas.price_flag_schema import FlaggedPriceSummary
from app.services.admin_list_service import AdminRecordPage, PAGE_SIZE


def flag_price_update(db: Session, user: User, price_update: PriceUpdate, reason: str | None) -> bool:
    """Record that a user flagged this price as looking wrong. Returns False instead
    of erroring if they already flagged it -- the unique constraint is there to stop
    duplicate rows, not to punish someone for tapping the button twice."""
    flag = PriceFlag(price_update_id=price_update.id, user_id=user.id, reason=reason)
    db.add(flag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    return True


def _flagged_statement():
    return (
        select(
            PriceFlag.price_update_id,
            Commodity.name.label("commodity_name"),
            Market.name.label("market_name"),
            func.count(PriceFlag.id).label("flag_count"),
            func.max(PriceFlag.created_at).label("latest_flag_at"),
        )
        .join(PriceUpdate, PriceUpdate.id == PriceFlag.price_update_id)
        .join(Commodity, Commodity.id == PriceUpdate.commodity_id)
        .join(Market, Market.id == PriceUpdate.market_id)
        .where(PriceFlag.resolved.is_(False))
        .group_by(PriceFlag.price_update_id, Commodity.name, Market.name)
        .order_by(func.max(PriceFlag.created_at).desc(), PriceFlag.price_update_id.desc())
    )


def list_flagged_price_updates(db: Session) -> list[FlaggedPriceSummary]:
    return [FlaggedPriceSummary(**row._mapping) for row in db.execute(_flagged_statement())]


def flagged_price_page(db: Session, *, offset: int) -> AdminRecordPage[FlaggedPriceSummary]:
    grouped = _flagged_statement().order_by(None).cte("flagged_groups")
    total = select(func.count().label("total")).select_from(grouped).cte("flagged_total")
    page = select(grouped).order_by(grouped.c.latest_flag_at.desc(), grouped.c.price_update_id.desc()).offset(offset).limit(PAGE_SIZE).cte("flagged_page")
    rows = db.execute(select(page, total.c.total).select_from(total).outerjoin(page, true())
        .order_by(page.c.latest_flag_at.desc(), page.c.price_update_id.desc())).mappings().all()
    return AdminRecordPage(items=[FlaggedPriceSummary(**row) for row in rows if row['price_update_id'] is not None],
                           total=rows[0]['total'], offset=offset)


def stream_flagged_prices(engine):
    def content():
        with Session(engine) as db:
            rows = db.execute(_flagged_statement().execution_options(yield_per=100))
            try:
                yield "["
                first = True
                for row in rows:
                    yield ("" if first else ",") + FlaggedPriceSummary(**row._mapping).model_dump_json()
                    first = False
                yield "]"
            finally:
                rows.close()
    return content()


def resolve_flags(db: Session, price_update_id: int, *, commit: bool = True) -> int:
    count = (
        db.query(PriceFlag)
        .filter(PriceFlag.price_update_id == price_update_id, PriceFlag.resolved.is_(False))
        .update({"resolved": True})
    )
    db.commit() if commit else db.flush()
    return count
