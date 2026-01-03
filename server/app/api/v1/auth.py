import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User, RefreshToken
from app.services.auth_service import hash_password, verify_password, create_access_token, create_refresh_token, hash_token
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Set up logger for authentication events
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create console handler if not exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize the limiter and add exception handler
limiter = Limiter(key_func=get_remote_address)

class UserRegister(BaseModel):
    email: EmailStr
    password: str  # Min 8 chars, 1 uppercase, 1 number (validation in endpoint)
    full_name: str | None = None
    institution: str | None = None

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")  # 3 attempts per hour per IP
async def register(request: Request, user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Validate password strength
    if len(user_data.password) < 8:
        logger.info(f"Registration failed - Password too short for email: {user_data.email} from IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in user_data.password):
        logger.info(f"Registration failed - Password missing uppercase for email: {user_data.email} from IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in user_data.password):
        logger.info(f"Registration failed - Password missing digit for email: {user_data.email} from IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    # Check duplicate email
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        logger.info(f"Registration failed - Email already exists: {user_data.email} from IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        institution=user_data.institution
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered successfully: {user_data.email} from IP: {request.client.host}")
    return user

@router.post("/login")
@limiter.limit("5/15minutes")  # 5 attempts per 15 minutes per IP
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Authenticate user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.info(f"Login failed - Invalid credentials for email: {form_data.username} from IP: {request.client.host}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.is_active:
        logger.info(f"Login failed - Account inactive for email: {form_data.username} from IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Inactive account")

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token()

    # Store refresh token
    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token_obj)
    await db.commit()

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=604800  # 7 days
    )

    logger.info(f"Login successful for email: {form_data.username} from IP: {request.client.host}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # This is the plain token for the response
        "token_type": "bearer",
        "expires_in": 1800
    }

@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    # Clear the refresh token cookie
    response.delete_cookie("refresh_token")
    logger.info(f"User logged out from IP: {request.client.host}")
    return {"message": "Logged out successfully"}

@router.post("/refresh")
async def refresh(request: Request, response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        logger.info(f"Token refresh failed - No refresh token provided from IP: {request.client.host}")
        raise HTTPException(status_code=401, detail="No refresh token provided")

    # Look up the refresh token in the database
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_token(refresh_token)
        ).where(
            RefreshToken.expires_at > datetime.utcnow()
        ).where(
            RefreshToken.revoked == False
        )
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        logger.info(f"Token refresh failed - Invalid refresh token from IP: {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Mark the old refresh token as revoked (rotation)
    token_record.revoked = True
    token_record.last_used_at = datetime.utcnow()

    # Create new tokens
    user = await db.get(User, token_record.user_id)
    new_access_token = create_access_token({"sub": user.email})
    new_refresh_token = create_refresh_token()

    # Store the new refresh token
    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(new_token_record)

    await db.commit()

    # Set the new refresh token in the cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=604800  # 7 days
    )

    logger.info(f"Token refresh successful for user ID: {token_record.user_id} from IP: {request.client.host}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }