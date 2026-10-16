import hashlib
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.revoked_access_token import RevokedAccessToken
from app.models.user import User


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_revoked(db: Session, token: str) -> bool:
    return db.get(RevokedAccessToken, token_digest(token)) is not None


def revoke_token(db: Session, user: User, token: str, *, expires_at: datetime) -> None:
    digest = token_digest(token)
    if db.get(RevokedAccessToken, digest) is not None:
        return
    db.add(RevokedAccessToken(token_hash=digest, user_id=user.id, expires_at=expires_at, revoked_at=datetime.now(timezone.utc)))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # A concurrent request can have already revoked this identical token.
        if db.get(RevokedAccessToken, digest) is None:
            raise
