"""
Chat router for RAG-powered robotics Q&A.
Supports streaming responses via Server-Sent Events.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.chat import ChatRequest, ChatResponse
from app.services.embedding import jina_service
from app.services.vector_db import qdrant_service
from app.services.ai_service import gemini_service
from uuid import uuid4
from app.db.base import get_db
from app.models.user import User
from app.models.chat_db import ChatSession, ChatMessage, MESSAGE_ROLE_USER, MESSAGE_ROLE_ASSISTANT
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process a chat query with RAG context.

    Args:
        request: ChatRequest with query and optional filters

    Returns:
        ChatResponse with AI-generated answer and sources
    """
    try:
        # Step 1: Generate query embedding
        query_embedding = await jina_service.generate_embedding(request.query)

        # Step 2: Retrieve relevant context from Qdrant
        context_chunks = await qdrant_service.search(
            query_vector=query_embedding, chapter_filter=request.chapter_filter
        )

        # Step 3: Generate response using Gemini
        response_text = await gemini_service.generate_response(
            query=request.query, context_chunks=context_chunks
        )

        # Step 4: Extract sources
        sources = [chunk["source_url"] for chunk in context_chunks]

        # Step 5: Save chat session and messages to database
        session_id = request.session_id or uuid4()

        # Check if session exists, otherwise create new one
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            # Create new session
            session = ChatSession(
                id=session_id,
                user_id=current_user.id,
                title=request.query[:255] if len(request.query) > 255 else request.query  # Use first part of query as title
            )
            db.add(session)

        # Create message objects
        user_message = ChatMessage(
            session_id=session_id,
            role=MESSAGE_ROLE_USER,
            content=request.query
        )
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=response_text
        )

        db.add(user_message)
        db.add(assistant_message)
        await db.commit()

        return ChatResponse(
            session_id=session_id,
            response=response_text,
            sources=sources,
        )

    except Exception as e:
        # Handle API quota/outage errors
        if "quota" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="AI service quota exceeded. Please try again later.",
                headers={"Retry-After": "3600"},
            )
        elif "429" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please slow down your requests.",
                headers={"Retry-After": "60"},
            )
        else:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Process a chat query with streaming response (SSE).

    Args:
        request: ChatRequest with query and optional filters

    Returns:
        StreamingResponse with SSE chunks
    """
    try:
        # Step 1: Generate query embedding
        query_embedding = await jina_service.generate_embedding(request.query)

        # Step 2: Retrieve relevant context
        context_chunks = await qdrant_service.search(
            query_vector=query_embedding, chapter_filter=request.chapter_filter
        )

        # Step 3: Stream response
        async def event_generator():
            async for chunk in gemini_service.generate_response_stream(
                query=request.query, context_chunks=context_chunks
            ):
                yield f"data: {chunk}\n\n"

            # Send sources at the end
            sources = [c["source_url"] for c in context_chunks]
            yield f"data: [SOURCES]{','.join(sources)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20
):
    """
    Get chat history for the authenticated user.
    """
    offset = (page - 1) * page_size

    # Get user's chat sessions
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    sessions = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    # Get message count for each session
    for session in sessions:
        msg_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
        )
        session.message_count = len(msg_result.scalars().all())

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "sessions": sessions
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,  # UUID as string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get messages for a specific chat session.
    """
    from uuid import UUID

    try:
        uuid_session_id = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Verify that the session belongs to the current user
    session_result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == uuid_session_id)
        .where(ChatSession.user_id == current_user.id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=403, detail="Session does not belong to user")

    # Get messages for the session
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == uuid_session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = messages_result.scalars().all()

    return {
        "session": session,
        "messages": messages
    }
