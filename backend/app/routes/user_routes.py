from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import AdminUserUpdate, UserResponse
from app.services.user_service import get_user, list_users, update_user
from app.utils.permissions import require_roles

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> list[User]:
    return list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> User:
    return get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> User:
    return update_user(db, get_user(db, user_id), payload)
