from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    full_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.student


class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserAdminUpdate(UserUpdate):
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
