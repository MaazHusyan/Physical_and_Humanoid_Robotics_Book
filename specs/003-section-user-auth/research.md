# Research: User Authentication & Authorization

**Feature**: User Authentication & Authorization
**Branch**: 003-section-user-auth
**Date**: 2026-01-02

## Overview

This document captures research findings for implementing secure user authentication in the FastAPI backend, informing technical decisions for the implementation plan.

## 1. JWT Token Management

### Decision: PyJWT with HS256 Algorithm

**Rationale**:
- python-jose is abandoned (last release ~3 years ago)
- FastAPI documentation updated to recommend PyJWT
- Actively maintained, lightweight, production-ready
- Install: `pip install pyjwt[crypto]`

**Alternatives Considered**:
- python-jose: Previously recommended but now abandoned
- authlib: More comprehensive but unnecessary complexity

**Implementation Pattern**:
- Access tokens: 15-30 minute lifespan
- Refresh tokens: 7-day lifespan with rotation
- HS256 algorithm (symmetric signing)

### Token Storage Strategy

**Decision**: httpOnly cookies for web, Authorization headers for API/mobile

**Rationale**:
- httpOnly cookies prevent XSS attacks (JavaScript can't access)
- Cookies with secure flag for HTTPS-only transmission
- Standard Bearer tokens remain available for mobile/SPA clients

**Security Features**:
- Refresh token rotation (one-time use)
- Token family tracking to detect theft
- Short-lived access tokens minimize exposure

## 2. Password Security

### Decision: Argon2 (Primary), bcrypt (Fallback)

**Rationale**:
- **Argon2**: Winner of Password Hashing Competition 2015
  - Configurable memory, time, parallelism
  - Resists GPU and custom hardware attacks
  - Recommended for new projects in 2026
- **bcrypt**: Battle-tested alternative
  - Standalone library actively maintained
  - 12-14 rounds for 2026 standards (~250-500ms hash time)
  - passlib has maintenance concerns (no release since 2020)

**Implementation**:
```python
# Argon2 (recommended)
from argon2 import PasswordHasher
ph = PasswordHasher(
    time_cost=3,       # iterations
    memory_cost=65536, # 64 MB
    parallelism=4,     # threads
    hash_len=32,
    salt_len=16
)
```

**Alternatives Considered**:
- passlib: Comprehensive but unmaintained, Python 3.13 compatibility issues
- pwdlib: Emerging replacement but less mature

## 3. Database & ORM

### Decision: PostgreSQL with SQLAlchemy 2.0 Async

**Rationale**:
- **PostgreSQL** chosen over SQLite for production:
  - Built-in authentication at database level
  - MVCC handles concurrent reads/writes without blocking
  - Thousands of concurrent connections
  - SQLite limitations: file-based, single writer, no network deployment
- **SQLAlchemy 2.0+** with async support:
  - Most mature ORM with extensive ecosystem
  - Native async/await in 2.0+
  - Seamless FastAPI integration
  - Excellent for complex auth/session queries

**Constitution Alignment**:
- Constitution specifies "FastAPI with Neon (Postgres)" ✅
- Using existing Postgres infrastructure from Section 2

**Alternatives Considered**:
- SQLite: Inadequate for multi-user production
- Tortoise ORM: Simpler but smaller ecosystem
- SQLModel: Considered but SQLAlchemy's flexibility preferred for auth complexity

**Database Schema Entities**:
- `users`: Core user accounts with role-based access
- `refresh_tokens`: Long-lived tokens for session renewal
- `chat_sessions`: Links conversations to users
- `chat_messages`: Individual messages within sessions

## 4. Rate Limiting

### Decision: SlowAPI (Development), fastapi-limiter (Production)

**Rationale**:
- **SlowAPI**:
  - Decorator-based, adapted from flask-limiter
  - In-memory, simple setup
  - Production-proven (millions of requests/month)
  - Perfect for single-instance deployments
- **fastapi-limiter**:
  - Redis-backed for distributed systems
  - Lua scripts for sophisticated limiting
  - Needed when scaling to multiple backend instances

**Implementation Pattern**:
- Login endpoint: 5 attempts per 15 minutes per IP
- Registration: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email

**Alternatives Considered**:
- Custom middleware: More maintenance overhead
- Cloud-based solutions: External dependencies

## 5. FastAPI Auth Patterns

### Decision: OAuth2PasswordBearer with Custom JWT Dependencies

**Rationale**:
- OAuth2PasswordBearer is FastAPI's standard pattern
- Automatic OpenAPI/Swagger integration
- Dependency injection for clean, testable code
- Follows official FastAPI security tutorial

**Dependency Chain**:
1. `oauth2_scheme`: Extract token from request
2. `get_current_user`: Validate JWT and fetch user from DB
3. `get_current_active_user`: Check user status (active/inactive)
4. `get_current_admin`: Verify admin role for protected routes

**Protected Route Pattern**:
```python
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
```

**Alternatives Considered**:
- fastapi-users library: Full auth solution but adds abstraction
- Custom decorators: Less idiomatic than dependency injection

## 6. Integration with Existing System

### Chat History Persistence

**Approach**: Extend existing chat endpoints to require authentication

**Changes Required**:
1. Update `ChatSession` model to include `user_id` foreign key
2. Modify `/api/v1/chat/` endpoints to accept authenticated user
3. Add `/api/v1/chat/history` endpoint for retrieving user's past conversations
4. Filter chat sessions by authenticated user ID

**Backward Compatibility**:
- Anonymous chat sessions remain supported (optional user_id)
- Existing Qdrant vector search unchanged
- RAG pipeline requires no modifications

### Database Migration Strategy

**Approach**: SQLAlchemy Alembic for schema versioning

**Migration Plan**:
1. Initialize Alembic in `/server` directory
2. Create initial migration with user/auth tables
3. Add migration to link chat_sessions to users (nullable user_id)
4. Future migrations for profile extensions

## Security Best Practices

### Implementation Checklist

1. **Environment Security**:
   - SECRET_KEY from environment variables (never commit)
   - Separate keys for development/production
   - Rotate secrets periodically

2. **Transport Security**:
   - HTTPS enforced in production
   - Secure flag on cookies
   - SameSite=Lax for CSRF protection

3. **Input Validation**:
   - Pydantic models for request validation
   - Email format validation
   - Password strength requirements (8+ chars, uppercase, number)
   - SQL injection prevention via SQLAlchemy parameterized queries

4. **Monitoring & Logging**:
   - Log authentication events (login, logout, failures)
   - Track failed login attempts for account lockout
   - Security event timestamps with user context

5. **Rate Limiting**:
   - Login endpoint: 5/15min per IP
   - Password change: 3/hour per user
   - Registration: 3/hour per IP

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| JWT Library | PyJWT | Latest | Actively maintained, FastAPI recommended |
| Password Hashing | Argon2 | Latest | 2026 best practice, memory-hard |
| Database | PostgreSQL | 14+ | Constitution-specified, production-ready |
| ORM | SQLAlchemy | 2.0+ | Async support, mature ecosystem |
| Rate Limiting | SlowAPI | Latest | Simple, production-proven |
| Auth Pattern | OAuth2PasswordBearer | Built-in | FastAPI standard |

## Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # Existing...
    "pyjwt[crypto]>=2.8.0",
    "argon2-cffi>=23.1.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",  # PostgreSQL async driver
    "alembic>=1.13.0",  # Database migrations
    "slowapi>=0.1.9",   # Rate limiting
    "python-multipart>=0.0.9",  # Form data support for OAuth2
]
```

## Open Questions Resolved

1. **Q**: SQLite vs PostgreSQL?
   **A**: PostgreSQL - Constitution specifies Postgres, and SQLite inadequate for multi-user production

2. **Q**: Which JWT library?
   **A**: PyJWT - python-jose abandoned, FastAPI now recommends PyJWT

3. **Q**: bcrypt vs Argon2?
   **A**: Argon2 for new implementations (2026 best practice), bcrypt as fallback

4. **Q**: Rate limiting approach?
   **A**: SlowAPI for simplicity, with documented migration path to fastapi-limiter + Redis

5. **Q**: Token storage method?
   **A**: httpOnly cookies for web (XSS protection), Bearer tokens for API/mobile

## References

- FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/
- PyJWT Migration Discussion: https://github.com/fastapi/fastapi/discussions/11345
- Argon2 Specification: https://github.com/P-H-C/phc-winner-argon2
- SQLAlchemy Async Guide: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
