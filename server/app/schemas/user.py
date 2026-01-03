from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.user import USER_ROLE_STUDENT, USER_ROLE_ADMIN, USER_ROLES


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    institution: Optional[str] = None
    role: str = USER_ROLE_STUDENT
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    users: list[UserResponse]