"""
Chat router for RAG-powered robotics Q&A.
Supports streaming responses via Server-Sent Events.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.embedding import jina_service
from app.services.vector_db import qdrant_service
from app.services.ai_service import gemini_service
from uuid import uuid4

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
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

        return ChatResponse(
            session_id=request.session_id or uuid4(),
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
