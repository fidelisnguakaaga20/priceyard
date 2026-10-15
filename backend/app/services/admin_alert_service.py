from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def notify_admins(db: Session, *, subject: str, body: str) -> None:
    """Email every active admin. Best-effort only - a failed send must never block the action that triggered it."""
    from hashlib import sha256
    from app.services.notification_service import enqueue_notification

    admins = db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True))).all()
    for admin in admins:
        enqueue_notification(db, channel="email", recipient=admin.email,
                             payload={"subject": subject, "body": body},
                             event_key="admin:" + sha256((subject + body).encode()).hexdigest())
