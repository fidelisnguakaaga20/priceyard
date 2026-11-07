"""TEMPORARY (owner-approved): proves error alerts reach the owner's email.

Opening /admin/test-alert while logged in as an admin causes one deliberate
server error, which Sentry reports by email. Remove after the alert is confirmed.
"""
from fastapi import APIRouter, Depends

from app.models.user import User
from app.utils.permissions import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


class PriceYardTestAlert(RuntimeError):
    pass


@router.get("/test-alert")
def trigger_test_alert(current_user: User = Depends(require_roles("admin"))) -> None:
    raise PriceYardTestAlert("PriceYard test alert - this deliberate error confirms that error emails work.")
