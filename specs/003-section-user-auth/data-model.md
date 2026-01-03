# Data Model: User Authentication & Authorization

**Feature**: User Authentication & Authorization
**Branch**: 003-section-user-auth
**Date**: 2026-01-02

## Overview

This document defines the data entities and their relationships for the user authentication system. All entities will be stored in PostgreSQL and managed via SQLAlchemy ORM.

## Entity Definitions

### 1. User

**Purpose**: Represents a registered user account with authentication credentials and profile information.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique user identifier |
| `email` | String(255) | Unique, Not Null, Indexed | User's email address (login credential) |
| `hashed_password` | String(255) | Not Null | Argon2/bcrypt hashed password |
| `full_name` | String(255) | Nullable | User's display name |
| `institution` | String(255) | Nullable | Educational institution (optional) |
| `role` | Enum | Not Null, Default='student' | User role: 'student' or 'admin' |
| `is_active` | Boolean | Not Null, Default=True | Account status (active/disabled) |
| `created_at` | Timestamp | Not Null, Default=NOW() | Account creation timestamp |
| `last_login_at` | Timestamp | Nullable | Most recent login timestamp |
| `updated_at` | Timestamp | Not Null, Default=NOW(), On Update | Last profile update timestamp |

**Indexes**:
- Primary: `id`
- Unique: `email`
- Index: `email` (for login queries)
- Index: `role` (for admin filtering)

**Validation Rules** (from FR-002):
- Email must match RFC 5322 format
- Password minimum 8 characters
- Password must contain at least one uppercase letter
- Password must contain at least one number

**Relationships**:
- One-to-Many with `RefreshToken` (user can have multiple active tokens)
- One-to-Many with `ChatSession` (user can have multiple conversation sessions)

---

### 2. RefreshToken

**Purpose**: Stores long-lived refresh tokens for session renewal with rotation support.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique token identifier |
| `user_id` | Integer | Foreign Key (users.id), Not Null, Indexed | Owner of this token |
| `token_hash` | String(255) | Unique, Not Null, Indexed | SHA-256 hash of refresh token |
| `expires_at` | Timestamp | Not Null, Indexed | Token expiration time (7 days from creation) |
| `revoked` | Boolean | Not Null, Default=False | Manual revocation flag |
| `created_at` | Timestamp | Not Null, Default=NOW() | Token creation timestamp |
| `last_used_at` | Timestamp | Nullable | Last time token was used for refresh |

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` → `users.id` (CASCADE on delete)
- Unique: `token_hash`
- Index: `expires_at` (for cleanup queries)
- Index: `user_id, revoked` (for active token lookup)

**Lifecycle**:
- Created: On successful login
- Used: When refreshing access token (marks `last_used_at`)
- Rotated: Old token marked `revoked=True`, new token created
- Expired: Automatically invalid after `expires_at`
- Revoked: On logout or security event

**Relationships**:
- Many-to-One with `User` (multiple tokens per user)

---

### 3. ChatSession

**Purpose**: Represents a conversation thread between a user and the AI tutor.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique session identifier |
| `user_id` | Integer | Foreign Key (users.id), Nullable, Indexed | Session owner (nullable for anonymous) |
| `title` | String(255) | Nullable | Conversation title (derived from first message) |
| `created_at` | Timestamp | Not Null, Default=NOW() | Session start timestamp |
| `updated_at` | Timestamp | Not Null, Default=NOW(), On Update | Last message timestamp |

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` → `users.id` (SET NULL on delete)
- Index: `user_id, updated_at` (for history retrieval sorted by recency)

**Migration Note**:
- Existing sessions without `user_id` remain valid (anonymous chats)
- New authenticated sessions will have `user_id` populated

**Relationships**:
- Many-to-One with `User` (multiple sessions per user)
- One-to-Many with `ChatMessage` (session contains multiple messages)

---

### 4. ChatMessage

**Purpose**: Individual messages within a chat session (user questions and AI responses).

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique message identifier |
| `session_id` | UUID | Foreign Key (chat_sessions.id), Not Null, Indexed | Parent conversation |
| `role` | Enum | Not Null | Message sender: 'user' or 'assistant' |
| `content` | Text | Not Null | Message text content |
| `created_at` | Timestamp | Not Null, Default=NOW() | Message timestamp |
| `model_used` | String(100) | Nullable | LLM model (e.g., 'groq/llama-3.3-70b') |
| `tokens_used` | Integer | Nullable | Token count for cost tracking |
| `sources` | JSONB | Nullable | Retrieved sources from RAG (array of URLs) |

**Indexes**:
- Primary: `id`
- Foreign Key: `session_id` → `chat_sessions.id` (CASCADE on delete)
- Index: `session_id, created_at` (for chronological message retrieval)

**Relationships**:
- Many-to-One with `ChatSession` (multiple messages per session)

---

### 5. AuthEvent (Optional - Security Auditing)

**Purpose**: Logs authentication events for security monitoring and compliance.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique event identifier |
| `user_id` | Integer | Foreign Key (users.id), Nullable, Indexed | User involved (null for failed logins) |
| `event_type` | Enum | Not Null, Indexed | Event: 'login', 'logout', 'login_failed', 'password_changed', 'token_refreshed' |
| `ip_address` | String(45) | Nullable | IPv4 or IPv6 address |
| `user_agent` | String(255) | Nullable | Browser/client user agent |
| `success` | Boolean | Not Null | Whether event succeeded |
| `failure_reason` | String(255) | Nullable | Error details for failed events |
| `created_at` | Timestamp | Not Null, Default=NOW(), Indexed | Event timestamp |

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` → `users.id` (SET NULL on delete)
- Index: `user_id, created_at` (for user activity timeline)
- Index: `event_type, created_at` (for security analytics)
- Index: `ip_address, created_at` (for IP-based rate limiting)

**Retention Policy**:
- Keep 90 days of audit logs
- Archive older logs to cold storage
- Use for account lockout after N failed attempts

**Relationships**:
- Many-to-One with `User` (multiple events per user)

---

## Entity Relationships Diagram

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│ email       │
│ password    │
│ role        │
│ ...         │
└─────┬───────┘
      │
      │ 1:N
      ├───────────────────────────┐
      │                           │
      │                           │
┌─────▼──────────┐      ┌────────▼──────────┐
│ RefreshToken   │      │  ChatSession      │
│────────────────│      │───────────────────│
│ id (PK)        │      │ id (PK)           │
│ user_id (FK)   │      │ user_id (FK, null)│
│ token_hash     │      │ title             │
│ expires_at     │      │ ...               │
│ ...            │      └────────┬──────────┘
└────────────────┘               │
                                 │ 1:N
                                 │
                        ┌────────▼───────────┐
                        │  ChatMessage       │
                        │────────────────────│
                        │ id (PK)            │
                        │ session_id (FK)    │
                        │ role               │
                        │ content            │
                        │ ...                │
                        └────────────────────┘

┌─────────────┐
│  AuthEvent  │
│─────────────│
│ id (PK)     │
│ user_id(FK) │  (Optional)
│ event_type  │
│ ...         │
└─────────────┘
```

## Enumerations

### UserRole

```python
class UserRole(str, Enum):
    STUDENT = "student"  # Default role for new registrations
    ADMIN = "admin"      # Full platform access
```

**Future Extensions**:
- `INSTRUCTOR`: Manage courses/content
- `MODERATOR`: Review user content

### MessageRole

```python
class MessageRole(str, Enum):
    USER = "user"        # User question
    ASSISTANT = "assistant"  # AI response
```

**Future Extensions**:
- `SYSTEM`: System messages (e.g., "Session started")

### AuthEventType

```python
class AuthEventType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    TOKEN_REFRESHED = "token_refreshed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
```

## State Transitions

### User Account States

```
[Registration] → ACTIVE (is_active=True)
     │
     ├─→ [Admin Disable] → INACTIVE (is_active=False)
     │                           │
     │                           └─→ [Admin Enable] → ACTIVE
     │
     └─→ [Delete Account] → DELETED (soft delete, record retained)
```

### Refresh Token States

```
[Login] → ACTIVE (revoked=False, not expired)
    │
    ├─→ [Token Refresh] → REVOKED (rotation)
    │
    ├─→ [Logout] → REVOKED
    │
    ├─→ [Expires] → EXPIRED (expires_at passed)
    │
    └─→ [Security Event] → REVOKED
```

### Chat Session States

```
[First Message] → ACTIVE (updated_at recent)
    │
    ├─→ [New Message] → ACTIVE (updated_at refreshed)
    │
    └─→ [User Delete] → DELETED (cascade delete messages)
```

## Database Migration Strategy

### Phase 1: Core Auth Tables

**Migration**: `001_create_auth_tables`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    institution VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMP
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
```

### Phase 2: Chat Integration

**Migration**: `002_link_chat_sessions_to_users`

```sql
ALTER TABLE chat_sessions
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id, updated_at DESC);
```

### Phase 3: Audit Logging (Optional)

**Migration**: `003_create_auth_events`

```sql
CREATE TABLE auth_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auth_events_user_id ON auth_events(user_id, created_at DESC);
CREATE INDEX idx_auth_events_type ON auth_events(event_type, created_at DESC);
CREATE INDEX idx_auth_events_ip ON auth_events(ip_address, created_at DESC);
```

## Data Validation Rules

### Email Validation
- Format: RFC 5322 compliant
- Uniqueness: Case-insensitive check
- Normalization: Lowercase before storage

### Password Validation (from spec FR-002)
- Minimum length: 8 characters
- Required: At least one uppercase letter
- Required: At least one number
- Optional (future): Special character requirement

### Token Generation
- Refresh tokens: 32-byte random value, URL-safe base64 encoded
- Store SHA-256 hash, not plaintext
- Access tokens: JWT with HS256 signature

## Sample Data

### Default Admin User

```python
# Created via migration script
User(
    email="admin@example.com",
    hashed_password="<argon2_hash>",
    full_name="System Administrator",
    role=UserRole.ADMIN,
    is_active=True
)
```

### Test Student User

```python
User(
    email="student@example.com",
    hashed_password="<argon2_hash>",
    full_name="Test Student",
    institution="MIT",
    role=UserRole.STUDENT,
    is_active=True
)
```

## Performance Considerations

### Query Optimization

1. **User Login**: Index on `email` ensures O(log n) lookup
2. **Token Validation**: Unique index on `token_hash` for fast refresh validation
3. **Chat History**: Composite index on `(user_id, updated_at DESC)` for paginated retrieval
4. **Expired Token Cleanup**: Index on `expires_at` for efficient batch deletion

### Scalability

- **Connection Pooling**: SQLAlchemy async engine with pool size 20-50
- **Read Replicas**: Separate read/write connections for high traffic
- **Token Cleanup**: Scheduled job to delete expired tokens (runs daily)
- **Audit Log Archival**: Move old auth_events to cold storage after 90 days

## Security Notes

1. **Password Storage**: Never store plaintext passwords, always use Argon2/bcrypt
2. **Token Storage**: Store SHA-256 hashes of refresh tokens, not plaintext
3. **Soft Deletes**: Consider soft delete for users (retain audit trail)
4. **PII Handling**: Email and full_name are personally identifiable information (GDPR compliance required)
5. **SQL Injection**: SQLAlchemy ORM provides protection via parameterized queries
