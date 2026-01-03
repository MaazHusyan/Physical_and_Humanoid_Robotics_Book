from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB


# Define role constants as strings instead of enum to avoid PostgreSQL enum issues
MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_ASSISTANT = "assistant"
MESSAGE_ROLES = [MESSAGE_ROLE_USER, MESSAGE_ROLE_ASSISTANT]


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Index for user-based queries
    title: Mapped[str | None] = mapped_column(String(255), index=True)  # Index for title-based searches
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Index for date-based queries
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # Index for updated date queries

    # Relationship to user (nullable for anonymous sessions)
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    # Relationship to messages
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_sessions.id"), index=True)  # Index for session-based queries
    role: Mapped[str] = mapped_column(String(50), index=True)  # Index for role-based queries
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)  # Index for date-based queries
    model_used: Mapped[str | None] = mapped_column(String(100), index=True)  # Index for model-based queries
    tokens_used: Mapped[int | None] = mapped_column(Integer, index=True)  # Index for token usage queries
    sources: Mapped[dict | None] = mapped_column(JSONB)  # Store as JSONB for PostgreSQL

    # Relationship to session
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")