import json

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment_schema import PaymentInitiateRequest, PaymentInitiateResponse, PaymentReconcileRequest, PaymentResponse
from app.services.payment_service import get_payment_status, handle_webhook_event, initiate_payment, list_payments, verify_webhook_signature
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/initiate", response_model=PaymentInitiateResponse)
def start_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentInitiateResponse:
    return initiate_payment(db, current_user, payload.plan)


@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, bool | str]:
    raw_body = await request.body()
    if len(raw_body) > 32768:
        raise HTTPException(status_code=413, detail="Payment event is too large")
    signature = request.headers.get("x-paystack-signature")
    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")

    outcome = handle_webhook_event(db, payload)
    return {"received": True, "outcome": outcome}


@router.post("/reconcile")
def reconcile_payment(
    payload: PaymentReconcileRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> dict[str, str]:
    raw_body = payload.signed_payload.encode("utf-8")
    if not verify_webhook_signature(raw_body, payload.signature):
        raise HTTPException(status_code=401, detail="Invalid provider evidence signature")
    try:
        event = json.loads(raw_body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid provider evidence") from exc
    outcome = handle_webhook_event(
        db, event, actor=admin,
        legacy_resolution=payload.legacy_resolution, reason=payload.reason,
    )
    return {"outcome": outcome}


@router.get("/status/{reference}", response_model=PaymentResponse)
def payment_status(
    reference: str = Path(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Payment:
    return get_payment_status(db, reference, user)


@router.get("", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[Payment]:
    return list_payments(db, offset=offset, limit=limit)
