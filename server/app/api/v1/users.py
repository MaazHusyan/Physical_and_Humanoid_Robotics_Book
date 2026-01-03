from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User
from app.api.dependencies import get_current_user, get_current_active_user
from app.services.auth_service import hash_password, verify_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["Profile"])

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.patch("/me")
async def update_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Update user fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.institution is not None:
        current_user.institution = user_update.institution

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return current_user

@router.post("/me/password")
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    if len(password_change.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in password_change.new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password_change.new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    # Update password
    current_user.hashed_password = hash_password(password_change.new_password)
    db.add(current_user)
    await db.commit()

    return {"message": "Password updated successfully"}


@router.get("/me/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active sessions for the current user.
    In this implementation, we're showing refresh tokens which represent active sessions.
    """
    from app.models.user import RefreshToken
    from datetime import datetime

    # Get all non-revoked refresh tokens for the user (active sessions)
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    active_tokens = result.scalars().all()

    return {
        "user_id": current_user.id,
        "active_sessions_count": len(active_tokens),
        "sessions": [
            {
                "id": token.id,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "last_used_at": token.last_used_at
            }
            for token in active_tokens
        ]
    }


@router.post("/me/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Log out from all devices by revoking all refresh tokens for the current user.
    """
    from app.models.user import RefreshToken
    from datetime import datetime

    # Revoke all non-expired refresh tokens for the user
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked = True
        token.last_used_at = datetime.utcnow()
        db.add(token)

    await db.commit()

    return {
        "message": f"Logged out from all devices. {len(tokens)} sessions terminated."
    }