from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription_schema import SubscriptionResponse, SubscriptionStatusUpdate
from app.services.audit_service import create_audit_log, snapshot_model
from app.services.admin_list_service import AdminJSONResponse, AdminRecordPage, admin_record_page, stream_admin_records
from app.services.subscription_service import (
    get_subscription_for_user,
    lock_subscription_state,
    apply_paid_expiry,
    apply_trial_expiry,
    expire_subscriptions_for_listing,
    send_trial_expiry_reminders,
    update_subscription_status,
)
from app.utils.permissions import get_current_user, require_roles

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def verify_cron_secret(x_cron_secret: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.cron_secret or x_cron_secret != settings.cron_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing cron secret")


@router.get("", response_model=list[SubscriptionResponse])
def get_subscriptions(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    expire_subscriptions_for_listing(db)
    return AdminJSONResponse(stream_admin_records(db.get_bind(), Subscription, SubscriptionResponse,
        order=(("id", False),)))


@router.get("/admin/page", response_model=AdminRecordPage[SubscriptionResponse])
def get_subscriptions_page(
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> AdminRecordPage[SubscriptionResponse]:
    expire_subscriptions_for_listing(db)
    return admin_record_page(db, Subscription, SubscriptionResponse, offset=offset, order=(("id", False),))


@router.get("/{user_id}", response_model=SubscriptionResponse)
def get_user_subscription(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Subscription:
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return get_subscription_for_user(db, user_id)


@router.post("/send-trial-reminders")
def trigger_trial_reminders(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> dict[str, int]:
    sent = send_trial_expiry_reminders(db)
    return {"sent": sent}


@router.post("/cron/send-trial-reminders")
def cron_trigger_trial_reminders(
    db: Session = Depends(get_db),
    _: None = Depends(verify_cron_secret),
) -> dict[str, int]:
    """Same job as /send-trial-reminders, but unlocked with a shared secret header
    (X-Cron-Secret) instead of an admin login, so an external scheduler can call it
    on a daily timer without needing to hold a user session."""
    sent = send_trial_expiry_reminders(db)
    return {"sent": sent}


@router.patch("/{user_id}/status", response_model=SubscriptionResponse)
def set_subscription_status(
    user_id: int,
    payload: SubscriptionStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> Subscription:
    user, subscription = lock_subscription_state(db, user_id)
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    old_subscription = snapshot_model(subscription)
    old_user = snapshot_model(user)
    try:
        apply_trial_expiry(subscription); apply_paid_expiry(subscription)
        subscription = update_subscription_status(db, subscription, payload.status, commit=False)
        create_audit_log(
            db, actor=admin, action="subscription.status_update", table_name="subscriptions",
            record_id=subscription.id, old_value=old_subscription, new_value=snapshot_model(subscription), commit=False,
        )
        new_user = snapshot_model(user)
        if old_user != new_user:
            create_audit_log(
                db, actor=admin, action="user.subscription_role_sync", table_name="users",
                record_id=user.id, old_value=old_user, new_value=new_user, commit=False,
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return subscription
