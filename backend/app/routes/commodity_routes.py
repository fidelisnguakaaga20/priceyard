from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commodity import Commodity
from app.models.user import User
from app.schemas.commodity_schema import CommodityCreate, CommodityResponse, CommodityUpdate
from app.services.commodity_service import (
    create_commodity,
    delete_commodity,
    get_commodity,
    list_commodities,
    update_commodity,
)
from app.utils.permissions import require_roles

router = APIRouter(prefix="/commodities", tags=["commodities"])


@router.get("", response_model=list[CommodityResponse])
def get_commodities(db: Session = Depends(get_db)) -> list[Commodity]:
    return list_commodities(db)


@router.get("/{commodity_id}", response_model=CommodityResponse)
def get_commodity_by_id(commodity_id: int, db: Session = Depends(get_db)) -> Commodity:
    return get_commodity(db, commodity_id)


@router.post("", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
def add_commodity(
    payload: CommodityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Commodity:
    return create_commodity(db, payload)


@router.patch("/{commodity_id}", response_model=CommodityResponse)
def edit_commodity(
    commodity_id: int,
    payload: CommodityUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Commodity:
    return update_commodity(db, get_commodity(db, commodity_id), payload)


@router.delete("/{commodity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_commodity(
    commodity_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    delete_commodity(db, get_commodity(db, commodity_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
