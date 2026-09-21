import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment_schema import PaymentInitiateRequest, PaymentInitiateResponse, PaymentResponse
from app.services.payment_service import handle_webhook_event, initiate_payment, list_payments, verify_webhook_signature
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
async def paystack_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature")
    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")

    handle_webhook_event(db, payload)
    return {"received": True}


@router.get("", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[Payment]:
    return list_payments(db)
