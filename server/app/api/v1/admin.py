from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User as UserModel, USER_ROLE_STUDENT, USER_ROLE_ADMIN, USER_ROLES
from app.api.dependencies import get_current_admin
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

router = APIRouter(prefix="/admin", tags=["Admin"])

# Define Pydantic models for API responses (separate from SQLAlchemy models)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    institution: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    updated_at: datetime

class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None

class AdminUserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    users: List[UserResponse]

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    current_user: UserModel = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size

    result = await db.execute(
        select(UserModel)
        .offset(offset)
        .limit(page_size)
    )
    db_users = result.scalars().all()

    # Convert SQLAlchemy models to Pydantic models
    user_responses = [
        UserResponse(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            institution=db_user.institution,
            role=db_user.role,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            last_login_at=db_user.last_login_at,
            updated_at=db_user.updated_at
        )
        for db_user in db_users
    ]

    # Get total count
    count_result = await db.execute(select(UserModel))
    total = len(count_result.scalars().all())

    return AdminUserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        users=user_responses
    )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        institution=user.institution,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        updated_at=user.updated_at
    )

@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    current_admin: UserModel = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Prevent admin from disabling their own account
    if user_id == current_admin.id and update_data.is_active is False:
        raise HTTPException(status_code=400, detail="Admin cannot disable their own account")

    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.role is not None:
        user.role = update_data.role

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        institution=user.institution,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        updated_at=user.updated_at
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: UserModel = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Prevent admin from deleting their own account
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Admin cannot delete their own account")

    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user (cascading will handle related refresh tokens and chat sessions)
    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}

@router.get("/stats")
async def get_admin_stats(
    current_user: UserModel = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.models.chat_db import ChatSession, ChatMessage
    from datetime import date

    # Get total users
    total_users_result = await db.execute(select(UserModel))
    total_users = len(total_users_result.scalars().all())

    # Get active users today (users who logged in today)
    today = date.today()
    active_users_result = await db.execute(
        select(UserModel)
        .where(
            UserModel.last_login_at.isnot(None),
            UserModel.last_login_at >= datetime.combine(today, datetime.min.time()),
            UserModel.last_login_at <= datetime.combine(today, datetime.max.time())
        )
    )
    active_users_today = len(active_users_result.scalars().all())

    # Get total chat sessions
    total_sessions_result = await db.execute(select(ChatSession))
    total_chat_sessions = len(total_sessions_result.scalars().all())

    # Get total messages
    total_messages_result = await db.execute(select(ChatMessage))
    total_messages = len(total_messages_result.scalars().all())

    return {
        "total_users": total_users,
        "active_users_today": active_users_today,
        "total_chat_sessions": total_chat_sessions,
        "total_messages": total_messages
    }