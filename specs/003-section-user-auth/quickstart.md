# Quickstart Guide: User Authentication & Authorization

**Feature**: User Authentication & Authorization
**Branch**: 003-section-user-auth
**Date**: 2026-01-02

## Overview

This guide provides step-by-step instructions for implementing the user authentication system, from database setup to testing protected endpoints.

## Prerequisites

- Python 3.12+ with `uv` package manager
- PostgreSQL 14+ running (local or cloud)
- Existing FastAPI backend from Section 2
- Environment variables configured

## Implementation Phases

### Phase 1: Database Setup

**Duration**: ~30 minutes

**Steps**:

1. **Install dependencies**:
```bash
cd server
uv add "pyjwt[crypto]>=2.8.0" "argon2-cffi>=23.1.0" "sqlalchemy[asyncio]>=2.0.0" "asyncpg>=0.29.0" "alembic>=1.13.0" "slowapi>=0.1.9" "python-multipart>=0.0.9"
```

2. **Initialize Alembic**:
```bash
cd server
alembic init alembic
```

3. **Configure Alembic** (`alembic/env.py`):
```python
from app.core.config import settings
from app.db.base import Base  # Will create this

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

4. **Create first migration**:
```bash
alembic revision -m "create auth tables"
# Edit migration file with SQL from data-model.md
alembic upgrade head
```

5. **Verify tables created**:
```bash
psql $DATABASE_URL -c "\dt"
# Should show: users, refresh_tokens tables
```

---

### Phase 2: Core Auth Module

**Duration**: ~1 hour

**Files to Create**:

1. **`server/app/db/base.py`** - SQLAlchemy base and models
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_maker() as session:
        yield session
```

2. **`server/app/models/user.py`** - User and RefreshToken models
```python
from sqlalchemy import String, Boolean, DateTime, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    institution: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
```

3. **`server/app/services/auth_service.py`** - Password hashing and token generation
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from datetime import datetime, timedelta
from app.core.config import settings
import secrets
import hashlib

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

4. **`server/app/api/v1/auth.py`** - Auth routes
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User, RefreshToken
from app.services.auth_service import hash_password, verify_password, create_access_token, create_refresh_token, hash_token
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str  # Min 8 chars, 1 uppercase, 1 number (validation in endpoint)
    full_name: str | None = None
    institution: str | None = None

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

    # Check duplicate email
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
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

    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Authenticate user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")

    # Update last login
    user.last_login_at = datetime.utcnow()

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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }
```

5. **`server/app/api/dependencies.py`** - Auth dependencies
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User, UserRole
import jwt
from app.core.config import settings
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
```

---

### Phase 3: Chat Integration

**Duration**: ~30 minutes

**Steps**:

1. **Create migration** to add `user_id` to `chat_sessions`:
```sql
ALTER TABLE chat_sessions
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id, updated_at DESC);
```

2. **Update chat models** (`server/app/models/chat.py`):
```python
from sqlalchemy import ForeignKey

class ChatSession(Base):
    # ... existing fields ...
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
```

3. **Modify chat endpoint** (`server/app/api/v1/chat.py`):
```python
from app.api.dependencies import get_current_user

@router.post("/chat/")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # Now required
    db: AsyncSession = Depends(get_db)
):
    # Associate session with user
    session.user_id = current_user.id
    # ... rest of logic
```

4. **Add chat history endpoint**:
```python
@router.get("/chat/history")
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    sessions = result.scalars().all()
    return {"sessions": sessions}
```

---

### Phase 4: Rate Limiting

**Duration**: ~15 minutes

**Steps**:

1. **Configure SlowAPI** (`server/main.py`):
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

2. **Apply rate limit to login** (`server/app/api/v1/auth.py`):
```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/15minutes")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # ... existing logic
```

---

### Phase 5: Environment Configuration

**Duration**: ~5 minutes

**Update `.env`**:
```bash
# Add to server/.env

# Database (already configured in Section 2)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/robotics_book

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here-generate-random-32-bytes

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Update `config.py`**:
```python
class Settings:
    def __init__(self):
        # ... existing settings ...

        # Auth Settings
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
```

---

## Testing

### Manual Testing with curl

**1. Register user**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123", "full_name": "Test User"}'
```

**2. Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"
```

**3. Access protected route**:
```bash
TOKEN="<access_token_from_login>"
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

**4. Test chat with auth**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is forward kinematics?"}'
```

### Automated Testing

**Create test file** (`server/tests/test_auth.py`):
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First register
        await client.post("/api/v1/auth/register", json={...})

        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "TestPass123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
```

**Run tests**:
```bash
cd server
uv run pytest tests/test_auth.py -v
```

---

## Verification Checklist

- [ ] Database tables created (users, refresh_tokens)
- [ ] User registration works with validation
- [ ] Login returns JWT tokens
- [ ] Protected routes require authentication
- [ ] Chat messages linked to users
- [ ] Chat history retrieval works
- [ ] Rate limiting active on login
- [ ] Token refresh mechanism works
- [ ] Logout invalidates tokens
- [ ] Admin routes restricted to admin role

---

## Troubleshooting

### Issue: "Could not validate credentials"
**Solution**: Check SECRET_KEY is set in .env and matches between token creation and validation

### Issue: "Connection refused" to PostgreSQL
**Solution**: Verify DATABASE_URL is correct and PostgreSQL is running

### Issue: "Password must contain uppercase"
**Solution**: Ensure password meets requirements (8+ chars, 1 uppercase, 1 number)

### Issue: Rate limit not working
**Solution**: Check SlowAPI is configured in main.py and limiter dependency is imported

---

## Next Steps

After completing implementation:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement tasks in priority order (P1 → P2 → P3 → P4)
3. Test each user story independently
4. Create PR for Section 3

---

## Reference Links

- FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic Migrations: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Argon2 Docs: https://argon2-cffi.readthedocs.io/
- SlowAPI: https://github.com/laurentS/slowapi
