from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.user import UserRead, UserUpdate
from app.schemas.user_settings import UserSettingsRead, UserSettingsUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current: User = Depends(get_current_user)) -> User:
    return current


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        password = data.pop("password")
        if password:
            current.hashed_password = hash_password(password)
    for key, value in data.items():
        setattr(current, key, value)
    db.commit()
    db.refresh(current)
    return current


@router.get("/me/settings", response_model=UserSettingsRead)
def get_my_settings(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSettings:
    if current.settings is None:
        current.settings = UserSettings(user_id=current.id)
        db.commit()
        db.refresh(current)
    return current.settings


@router.patch("/me/settings", response_model=UserSettingsRead)
def update_my_settings(
    payload: UserSettingsUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSettings:
    if current.settings is None:
        current.settings = UserSettings(user_id=current.id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current.settings, key, value)
    db.commit()
    db.refresh(current.settings)
    return current.settings
