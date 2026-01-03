from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base

# Define role constants as strings instead of enum to avoid PostgreSQL enum issues
USER_ROLE_STUDENT = "student"
USER_ROLE_ADMIN = "admin"
USER_ROLES = [USER_ROLE_STUDENT, USER_ROLE_ADMIN]

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), index=True)  # Index for search by name
    institution: Mapped[str | None] = mapped_column(String(255), index=True)  # Index for search by institution
    role: Mapped[str] = mapped_column(String(50), default=USER_ROLE_STUDENT, index=True)  # Index for role-based queries
    is_active: Mapped[bool] = mapped_column(default=True, index=True)  # Index for active/inactive queries
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Index for date-based queries
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)  # Index for login activity queries
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)  # Index for user-based queries
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)  # Index for expiration queries
    revoked: Mapped[bool] = mapped_column(default=False, index=True)  # Index for revoked status queries
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Index for date-based queries
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)  # Index for usage tracking

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")