from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.buying_zone import BuyingZone
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.user import User
from app.schemas.buying_zone_schema import BuyingZoneCreate, BuyingZoneUpdate


def _validate_active_market_scope(db: Session, *, commodity_id: int, market_id: int) -> None:
    commodity = db.get(Commodity, commodity_id)
    if commodity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")
    if not commodity.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Commodity is inactive")

    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    if not market.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Market is inactive")


def _validate_buying_zone_values(
    *,
    price_low: Decimal,
    price_high: Decimal,
    valid_from,
    valid_to,
) -> None:
    if price_low < 0 or price_high < price_low:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid buying-zone price range",
        )
    if valid_from is not None and valid_to is not None and valid_to < valid_from:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="valid_to must be on or after valid_from",
        )


def create_buying_zone(db: Session, payload: BuyingZoneCreate, admin: User) -> BuyingZone:
    _validate_active_market_scope(db, commodity_id=payload.commodity_id, market_id=payload.market_id)
    _validate_buying_zone_values(
        price_low=payload.price_low,
        price_high=payload.price_high,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
    )
    zone = BuyingZone(**payload.model_dump(), created_by=admin.id)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_buying_zone(db: Session, zone_id: int) -> BuyingZone:
    zone = db.get(BuyingZone, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buying zone not found")
    return zone


def list_buying_zones(db: Session) -> list[BuyingZone]:
    return list(db.scalars(select(BuyingZone).order_by(BuyingZone.created_at.desc(), BuyingZone.id.desc())).all())


def update_buying_zone(db: Session, zone: BuyingZone, payload: BuyingZoneUpdate) -> BuyingZone:
    changes = payload.model_dump(exclude_unset=True)
    commodity_id = int(changes.get("commodity_id", zone.commodity_id))
    market_id = int(changes.get("market_id", zone.market_id))
    price_low = changes.get("price_low", zone.price_low)
    price_high = changes.get("price_high", zone.price_high)
    valid_from = changes.get("valid_from", zone.valid_from)
    valid_to = changes.get("valid_to", zone.valid_to)

    _validate_active_market_scope(db, commodity_id=commodity_id, market_id=market_id)
    _validate_buying_zone_values(
        price_low=Decimal(price_low),
        price_high=Decimal(price_high),
        valid_from=valid_from,
        valid_to=valid_to,
    )

    for field, value in changes.items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    return zone
