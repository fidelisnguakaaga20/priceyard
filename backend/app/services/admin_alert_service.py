from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def notify_admins(db: Session, *, subject: str, body: str) -> None:
    """Email every active admin. Best-effort only - a failed send must never block the action that triggered it."""
    from app.services.email_service import send_email

    admins = db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True))).all()
    for admin in admins:
        try:
            send_email(recipient=admin.email, subject=subject, body=body)
        except Exception:
            continue
