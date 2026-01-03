# ADR-0001: Authentication Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-02
- **Feature:** User Authentication & Authorization
- **Context:** Need to implement secure user authentication and authorization for the robotics textbook platform. The solution must integrate with existing FastAPI backend, provide JWT-based authentication with refresh token rotation, secure password hashing, and role-based access control.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Authentication technology stack for the user authentication system:

- **JWT Library**: PyJWT with HS256 algorithm for token generation and validation
- **Password Hashing**: Argon2 (memory-hard) with configurable parameters for secure password storage
- **Database**: PostgreSQL with SQLAlchemy 2.0 async ORM for user data and session management
- **Rate Limiting**: SlowAPI for protection against brute force attacks on authentication endpoints
- **Auth Pattern**: OAuth2PasswordBearer with FastAPI dependency injection for protected routes
- **Token Storage**: httpOnly cookies for refresh tokens, Bearer tokens for access tokens

## Consequences

### Positive

- Industry-standard, well-maintained libraries with active communities
- Strong security posture with memory-hard password hashing (Argon2) and short-lived JWT tokens
- Seamless integration with existing FastAPI infrastructure and async patterns
- XSS protection through httpOnly cookies for refresh tokens
- Flexible role-based access control via dependency injection chain
- Built-in OpenAPI/Swagger documentation for authentication endpoints
- Proper async support for high-concurrency authentication requests

### Negative

- Argon2 hashing is slower than bcrypt (~250-500ms vs ~100-200ms), potentially impacting performance under high load
- Learning curve for developers unfamiliar with FastAPI dependency injection patterns
- Additional complexity with token refresh and rotation mechanisms
- Need for additional infrastructure considerations (token cleanup jobs, rate limiting storage)
- Dependency on multiple libraries that need to be kept up-to-date for security

## Alternatives Considered

Alternative Stack A: python-jose + bcrypt + SQLite + Custom rate limiting
- Why rejected: python-jose is abandoned, bcrypt is considered legacy, SQLite inadequate for multi-user production, custom rate limiting adds maintenance overhead

Alternative Stack B: Authlib + passlib + SQLModel + fastapi-limiter
- Why rejected: Authlib adds unnecessary complexity for basic auth, passlib has maintenance concerns, SQLModel less flexible than SQLAlchemy for auth complexity, fastapi-limiter requires Redis setup initially

Alternative Stack C: fastapi-users library + SQLModel
- Why rejected: Adds abstraction layer that might not align with custom requirements, less control over security implementation details

## References

- Feature Spec: /home/maaz/Desktop/Physical_and_Humanoid_Robotics_Book/specs/003-section-user-auth/spec.md
- Implementation Plan: /home/maaz/Desktop/Physical_and_Humanoid_Robotics_Book/specs/003-section-user-auth/plan.md
- Related ADRs: None
- Evaluator Evidence: /home/maaz/Desktop/Physical_and_Humanoid_Robotics_Book/specs/003-section-user-auth/research.md
