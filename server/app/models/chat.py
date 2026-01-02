"""
Pydantic models for chat and knowledge management.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class KnowledgeChunk(BaseModel):
    """Represents a vectorized segment of robotics book content."""

    id: UUID = Field(default_factory=uuid4)
    text: str = Field(..., description="Markdown text content")
    vector: Optional[List[float]] = Field(None, description="1024-dim embedding vector")
    chapter_id: str = Field(..., description="Chapter slug (e.g., 'kinematics')")
    title: str = Field(..., description="Section/header title")
    source_url: str = Field(..., description="URL to Docusaurus page")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "The Jacobian matrix relates joint velocities to end-effector velocities...",
                "chapter_id": "kinematics",
                "title": "Jacobian Matrices",
                "source_url": "/docs/kinematics#jacobian-matrices",
            }
        }


class Message(BaseModel):
    """Represents a single chat message."""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatSession(BaseModel):
    """Represents a conversation session."""

    session_id: UUID = Field(default_factory=uuid4)
    messages: List[Message] = Field(default_factory=list)
    context_chunks: List[UUID] = Field(
        default_factory=list, description="Knowledge chunks used in session"
    )


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[UUID] = None
    chapter_filter: Optional[str] = Field(
        None, description="Optional chapter to filter context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    session_id: UUID
    response: str
    sources: List[str] = Field(default_factory=list, description="Source URLs used")
