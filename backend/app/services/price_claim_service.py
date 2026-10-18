"""Owner-approved evidence checks for new claims, never historical rewrites."""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.price_update import PriceUpdate

UNKNOWN_SPECIFICATIONS = frozenset({"", "unknown", "not known", "not specified", "not confirmed",
    "not available", "not provided", "n/a", "na", "none", "unspecified", "\u2014", "-", "?"})
MOVEMENT_INPUTS = frozenset({"movement", "commodity_id", "market_id", "unit", "bag_size", "commodity_type",
    "price_low", "price_high", "previous_price_low", "previous_price_high", "update_date_time"})
CONFIDENCE_INPUTS = frozenset({"confidence_level", "source_1", "source_2", "commodity_id", "market_id",
    "unit", "bag_size", "commodity_type", "price_low", "price_high", "update_date_time"})


def validate_price_claims(db: Session, values: dict, *, record_id: int | None = None,
                          movement: bool = True, confidence: bool = True) -> None:
    if confidence and values['confidence_level'] == 'Verified by 2 sources':
        references = [str(values.get(name) or '').strip().casefold() for name in ('source_1', 'source_2')]
        if not all(references) or references[0] == references[1]:
            raise HTTPException(status_code=422, detail='Verified by 2 sources requires two different references in the private source fields.')
    if not movement or values['movement'] == 'unknown':
        return
    specifications = {name: str(values.get(name) or '').strip().lower() for name in ('unit', 'bag_size', 'commodity_type')}
    previous = None
    if all(value not in UNKNOWN_SPECIFICATIONS for value in specifications.values()):
        statement = select(PriceUpdate.price_low, PriceUpdate.price_high).where(
            PriceUpdate.commodity_id == values['commodity_id'], PriceUpdate.market_id == values['market_id'],
            PriceUpdate.status == 'approved', PriceUpdate.is_outdated.is_(False),
            PriceUpdate.update_date_time < values['update_date_time'],
            *(func.lower(func.trim(getattr(PriceUpdate, name))) == value for name, value in specifications.items()),
        )
        if record_id is not None:
            statement = statement.where(PriceUpdate.id != record_id)
        previous = db.execute(statement.order_by(PriceUpdate.update_date_time.desc(), PriceUpdate.id.desc()).limit(1)).first()
    expected = 'unknown'
    if previous is not None:
        low, high = Decimal(values['price_low']), Decimal(values['price_high'])
        prior_low, prior_high = previous
        if low > prior_low and high > prior_high: expected = 'up'
        elif low < prior_low and high < prior_high: expected = 'down'
        elif low == prior_low and high == prior_high: expected = 'stable'
        supplied = (values.get('previous_price_low'), values.get('previous_price_high'))
        if supplied != (None, None) and supplied != (prior_low, prior_high): expected = 'unknown'
    if values['movement'] != expected:
        raise HTTPException(status_code=422, detail='Movement is not supported by the preceding comparable approved price. Choose unknown or correct the claim and its recorded inputs.')


def model_claim_values(item: PriceUpdate, changes: dict | None = None) -> dict:
    names = MOVEMENT_INPUTS | CONFIDENCE_INPUTS
    return {name: (changes or {}).get(name, getattr(item, name)) for name in names}
