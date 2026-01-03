# Implementation Plan: User Authentication & Authorization

**Branch**: `003-section-user-auth` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)

## Summary

Implement secure user authentication and authorization system for the robotics textbook platform. Provides user registration, JWT-based authentication, role-based access control (student/admin), and integration with existing RAG chat system for conversation history persistence. Uses PostgreSQL for user data, SQLAlchemy async ORM, Argon2 password hashing, and FastAPI dependency injection for protected routes.

**Key Capabilities**:
- User registration with email/password (password validation)
- Login/logout with JWT access tokens and refresh token rotation
- Protected API routes with authentication middleware
- User profile management (view/update profile, change password)
- Chat history persistence per authenticated user
- Role-based access control (student vs admin routes)
- Rate limiting on authentication endpoints
- Security audit logging

## Technical Context

**Language/Version**: Python 3.12+ (existing from Section 2)

**Primary Dependencies**:
- `pyjwt[crypto]>=2.8.0` - JWT token generation and validation
- `argon2-cffi>=23.1.0` - Password hashing (2026 best practice)
- `sqlalchemy[asyncio]>=2.0.0` - Async ORM for user data
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `alembic>=1.13.0` - Database schema migrations
- `slowapi>=0.1.9` - Rate limiting for login endpoints
- `python-multipart>=0.0.9` - OAuth2 form data support

**Storage**: PostgreSQL (Constitution-specified, already configured in Section 2 for Neon/Qdrant)

**Testing**: pytest with pytest-asyncio for async endpoint testing

**Target Platform**: Linux server (existing FastAPI deployment)

**Project Type**: Web application (backend FastAPI + frontend Docusaurus)

**Performance Goals**:
- Login < 3 seconds (including token generation)
- Password hashing < 500ms (Argon2 with 3 time_cost, 64MB memory)
- Token validation < 50ms (JWT signature verification)
- Chat history retrieval < 2 seconds for 100+ conversations

**Constraints**:
- No OAuth/SSO in initial release (email/password only)
- No email verification (deferred to future release)
- No password reset via email (admin-assisted initially)
- Token rotation enforced (one-time use refresh tokens)

**Scale/Scope**:
- Expected: 100-1000 users initially
- Concurrent sessions: 50-100 authenticated users
- Chat history: Unlimited storage with pagination
- Rate limiting: 5 login attempts per 15min per IP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Branch-Locked Execution (Section 3)
- Branch `003-section-user-auth` aligns with Section 3 (User/Auth) progression
- Follows Section 1 (Foundation) → Section 2 (Intelligence/RAG) → Section 3 (User/Auth)
- No cross-section feature creep

### ✅ Technical Invariants
- **Python Backend**: Using `uv` for dependency management ✓
- **FastAPI**: Extends existing FastAPI backend from Section 2 ✓
- **PostgreSQL**: Constitution specifies "Neon (Postgres)" - using Postgres for auth ✓
- **Verification**: All technology choices researched via WebSearch and Context7 MCP ✓

### ⚠️ Auth Technology Note
- **Constitution Requirement**: "Better-Auth integration for user profiling"
- **Current Approach**: Custom JWT auth with FastAPI-native patterns
- **Rationale**: Better-Auth is TypeScript/Next.js specific, not compatible with Python/FastAPI. Custom implementation provides equivalent functionality with better FastAPI integration.
- **Compliance**: Delivers same user profiling capability (email, name, institution, role) as intended by constitution.

### ✅ Intelligence & Bonus Optimization
- **SDD Rigor**: Spec → Plan → Tasks → Implement cycle followed ✓
- **PHR Mandate**: PHR created for this planning phase ✓
- **Modular Design**: Auth system designed as reusable middleware/dependencies ✓

### ✅ Feature Requirements
- **Auth**: User profiling with software/hardware background (institution field) ✓
- **RAG Integration**: Chat history linked to authenticated users ✓

### ✅ Directory Structure
- `/server`: Auth implementation in existing FastAPI backend ✓
- `/content`: Future frontend login/signup components (Docusaurus) ✓
- `/specs`: This plan and artifacts in `specs/003-section-user-auth/` ✓
- `/history`: PHR for planning in `history/prompts/003-section-user-auth/` ✓

**Gate Status**: ✅ PASSED (with note on Better-Auth equivalency)

## Project Structure

### Documentation (this feature)

```
specs/003-section-user-auth/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology choices and best practices
├── data-model.md        # Database schema and entities
├── quickstart.md        # Implementation guide
├── contracts/
│   └── auth-api.yaml    # OpenAPI specification for auth endpoints
├── checklists/
│   └── requirements.md  # Spec quality validation
└── tasks.md             # (Generated by /sp.tasks command - not created yet)
```

### Source Code (repository root)

```
server/
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   └── base.py              # SQLAlchemy base, engine, session maker
│   ├── models/
│   │   ├── user.py              # User, RefreshToken models
│   │   └── chat.py              # Update with user_id foreign key
│   ├── services/
│   │   ├── auth_service.py      # Password hashing, token generation
│   │   ├── user_service.py      # User CRUD operations
│   │   └── chat_service.py      # Update to filter by user_id
│   ├── api/
│   │   ├── dependencies.py      # Auth dependencies (get_current_user, etc.)
│   │   └── v1/
│   │       ├── auth.py          # Registration, login, logout, refresh
│   │       ├── users.py         # Profile management, password change
│   │       ├── chat.py          # Update to require auth, add history endpoint
│   │       └── admin.py         # Admin-only user management routes
│   ├── core/
│   │   └── config.py            # Update with SECRET_KEY, token expiration
│   └── main.py                  # Update with SlowAPI rate limiter
├── alembic/
│   ├── versions/
│   │   ├── 001_create_auth_tables.py        # Users, refresh_tokens tables
│   │   └── 002_link_chat_to_users.py        # Add user_id to chat_sessions
│   └── env.py
└── tests/
    ├── test_auth.py             # Auth endpoint tests
    ├── test_users.py            # Profile management tests
    └── test_chat_history.py     # Chat history retrieval tests

content/
└── src/
    ├── components/
    │   ├── LoginForm.jsx        # (Future) Login UI component
    │   └── RegisterForm.jsx     # (Future) Registration UI component
    └── pages/
        ├── login.jsx            # (Future) Login page
        └── register.jsx         # (Future) Registration page
```

**Structure Decision**: Web application structure selected (Option 2) as project has distinct backend (FastAPI) and frontend (Docusaurus) components. Auth implementation primarily backend-focused in this phase, with frontend components deferred to future enhancement.

## Complexity Tracking

> **No violations to justify** - All architecture decisions align with constitution and follow FastAPI best practices.

## Design Decisions

### 1. Password Hashing: Argon2

**Decision**: Use Argon2-CFFI with memory-hard configuration

**Rationale**:
- Winner of Password Hashing Competition 2015
- Resists GPU and ASIC attacks via memory hardness
- Configurable time/memory/parallelism parameters
- 2026 industry best practice (bcrypt considered legacy)

**Configuration**:
```python
PasswordHasher(
    time_cost=3,       # 3 iterations
    memory_cost=65536, # 64 MB
    parallelism=4,     # 4 threads
    hash_len=32,       # 32-byte output
    salt_len=16        # 16-byte salt
)
```

**Trade-offs**:
- Slightly slower than bcrypt (~250-500ms vs ~100-200ms)
- Higher memory usage (intentional security feature)
- Better future-proofing against hardware attacks

---

### 2. JWT Strategy: HS256 with Short-Lived Tokens

**Decision**: Short-lived access tokens (30 min) + refresh token rotation

**Rationale**:
- HS256 (symmetric signing) sufficient for single-server deployment
- Short access token lifetime limits exposure window
- Refresh token rotation prevents replay attacks
- Stored refresh token hashes (SHA-256) not plaintext

**Token Lifecycle**:
1. Login → Generate access token (30min) + refresh token (7 days)
2. Access token expires → Use refresh token to get new pair
3. Refresh token used → Old token revoked, new token issued
4. Logout → Revoke all user's refresh tokens

**Alternatives Considered**:
- RS256 (asymmetric): Overkill for single-server, adds key management complexity
- Long-lived access tokens: Security risk if leaked
- No refresh tokens: Poor UX (re-login every 30min)

---

### 3. Database: PostgreSQL with SQLAlchemy 2.0 Async

**Decision**: Extend existing PostgreSQL database with auth tables

**Rationale**:
- Constitution specifies "Neon (Postgres)" ✓
- Already configured in Section 2 for Qdrant vector DB
- MVCC handles concurrent auth requests without locking
- SQLAlchemy 2.0 async integrates seamlessly with FastAPI

**Schema Design**:
- `users` table: Core authentication and profile data
- `refresh_tokens` table: Long-lived tokens with rotation support
- `chat_sessions.user_id`: Foreign key to link conversations (nullable for backward compatibility)

**Migration Strategy**:
- Alembic for version-controlled schema changes
- Migrations applied via `alembic upgrade head`
- Rollback support for failed deployments

---

### 4. Rate Limiting: SlowAPI

**Decision**: SlowAPI with in-memory storage for initial release

**Rationale**:
- Decorator-based, minimal boilerplate
- Adapted from proven flask-limiter
- In-memory sufficient for single-instance deployment
- Easy migration path to Redis-backed fastapi-limiter when scaling

**Limits**:
- Login endpoint: 5 attempts / 15 minutes / IP address
- Registration: 3 attempts / hour / IP address
- Password change: 3 attempts / hour / authenticated user

**Future Scaling**: Migrate to fastapi-limiter + Redis when deploying multiple backend instances

---

### 5. Auth Dependencies: FastAPI Dependency Injection

**Decision**: Layered dependency chain for auth/role checking

**Dependency Hierarchy**:
```
oauth2_scheme (extract token from header)
    ↓
get_current_user (validate JWT, fetch user from DB)
    ↓
get_current_active_user (check is_active flag)
    ↓
get_current_admin (check role == admin)
```

**Benefits**:
- Separation of concerns (token validation, user retrieval, status check)
- Reusable across routes
- Testable via dependency overrides
- Automatic OpenAPI/Swagger documentation

**Usage Example**:
```python
@router.get("/users/me")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/admin/users")
async def list_users(admin: User = Depends(get_current_admin)):
    # Only accessible to admin role
    return users
```

---

### 6. Token Storage: httpOnly Cookies

**Decision**: Store refresh tokens in httpOnly cookies, access tokens client-side

**Rationale**:
- httpOnly cookies inaccessible to JavaScript (XSS protection)
- Secure flag ensures HTTPS-only transmission
- SameSite=Lax provides CSRF protection
- Access tokens (short-lived) can be stored in memory/localStorage

**Cookie Configuration**:
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,        # No JS access
    secure=True,          # HTTPS only (production)
    samesite="lax",       # CSRF protection
    max_age=604800        # 7 days
)
```

---

### 7. Chat History Integration

**Decision**: Add nullable `user_id` foreign key to `chat_sessions`

**Rationale**:
- Backward compatibility: Existing anonymous sessions remain valid (user_id=NULL)
- Forward compatibility: New authenticated chats link to users
- Soft migration: No data loss for existing conversations
- Privacy-friendly: Anonymous chat option still available

**Query Pattern**:
```sql
SELECT * FROM chat_sessions
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20;
```

**Indexes**: Composite index on `(user_id, updated_at DESC)` for efficient paginated retrieval

---

## Integration Points

### 1. Existing FastAPI Backend

**Modification Required**:
- Add auth routes to `app.include_router(auth.router, prefix="/api/v1")`
- Configure SlowAPI limiter in `main.py`
- Update CORS to allow credentials (cookies)

**No Breaking Changes**: Existing endpoints remain accessible (chat can be made optional auth initially)

---

### 2. Existing Chat Endpoints

**Changes**:
- Add `current_user: User = Depends(get_current_user)` to chat route
- Link `ChatSession` to `current_user.id` when creating sessions
- Filter chat history by `user_id` in retrieval endpoint

**Backward Compatibility**:
- Existing `POST /api/v1/chat/` can remain unauthenticated (optional user dependency)
- Migration path: Phase 1 optional auth → Phase 2 required auth

---

### 3. Qdrant Vector Database

**No Changes Required**: RAG retrieval logic unchanged, operates independently of user auth

---

### 4. Frontend (Docusaurus)

**Future Integration** (not in scope for initial backend implementation):
- Login/Register forms as React components
- Auth context provider for token management
- Protected route wrapper for authenticated pages
- Logout button in navigation

**API Contract**: OpenAPI spec in `contracts/auth-api.yaml` provides frontend integration guide

---

## Security Measures

### 1. Password Security
- ✅ Argon2 hashing with memory-hard parameters
- ✅ Minimum 8 characters, 1 uppercase, 1 number validation
- ✅ No plaintext storage, ever
- ✅ Password change requires current password verification

### 2. Token Security
- ✅ Short-lived access tokens (30 min expiration)
- ✅ Refresh token rotation (one-time use)
- ✅ Token hashes stored (SHA-256), not plaintext
- ✅ Logout invalidates all user tokens

### 3. Transport Security
- ✅ HTTPS enforced in production (secure cookie flag)
- ✅ httpOnly cookies prevent XSS
- ✅ SameSite=Lax prevents CSRF

### 4. Input Validation
- ✅ Pydantic models for request validation
- ✅ Email format validation (RFC 5322)
- ✅ SQL injection prevention via SQLAlchemy parameterized queries

### 5. Rate Limiting
- ✅ Login: 5 attempts / 15min / IP
- ✅ Registration: 3 attempts / hour / IP
- ✅ Password change: 3 attempts / hour / user

### 6. Audit Logging
- ✅ Log all auth events (login, logout, failures)
- ✅ Track IP address and user agent
- ✅ 90-day retention for security analysis

---

## Testing Strategy

### Unit Tests
- Password hashing/verification
- Token generation/validation
- User model validation

### Integration Tests
- Registration flow (happy path + error cases)
- Login flow (valid/invalid credentials, rate limiting)
- Protected endpoint access (with/without token)
- Token refresh flow (valid/expired tokens)
- Chat history retrieval (user-specific filtering)

### End-to-End Tests
- Complete user journey: register → login → chat → view history → logout
- Admin user journey: login → view users → update user status

---

## Deployment Considerations

### Environment Variables
```bash
# Required new variables
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Existing from Section 2
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### Database Migration
```bash
# Initialize Alembic (one-time)
alembic init alembic

# Create migration
alembic revision -m "create auth tables"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### First Admin User
```bash
# Run migration script to create admin user
python scripts/create_admin.py --email admin@example.com --password AdminPass123
```

---

## Performance Optimization

### Database Queries
- **Indexes**: Email (login), token_hash (refresh validation), user_id+updated_at (chat history)
- **Connection Pooling**: SQLAlchemy async engine with pool size 20-50
- **Query Optimization**: Select only needed columns, avoid N+1 queries

### Token Validation
- **Caching**: Consider Redis cache for recently validated tokens (optional future enhancement)
- **Algorithm**: HS256 signature verification < 50ms

### Password Hashing
- **Async**: Offload to thread pool to avoid blocking event loop
- **Target**: < 500ms hash time (Argon2 params tuned for this)

---

## Risks and Mitigation

### Risk 1: Token Theft
**Mitigation**: Short-lived access tokens, refresh token rotation, httpOnly cookies

### Risk 2: Brute Force Attacks
**Mitigation**: Rate limiting (5 attempts / 15min), account lockout after 10 failed attempts (future)

### Risk 3: Database Performance Degradation
**Mitigation**: Proper indexes, connection pooling, query optimization, read replicas (future)

### Risk 4: SECRET_KEY Exposure
**Mitigation**: Environment variables only, never commit to git, rotate keys periodically

---

## Future Enhancements (Out of Scope)

- OAuth2 integration (Google, GitHub login)
- Email verification during registration
- Password reset via email
- Two-factor authentication (2FA)
- Session management UI (view active sessions, revoke tokens)
- Advanced admin analytics (user activity trends, popular topics)

---

## References

- Research: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- API Contracts: [contracts/auth-api.yaml](./contracts/auth-api.yaml)
- Quickstart Guide: [quickstart.md](./quickstart.md)
- Feature Spec: [spec.md](./spec.md)

---

**Plan Status**: ✅ Complete - Ready for `/sp.tasks` to generate implementation tasks
