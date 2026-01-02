from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.services.vector_db import qdrant_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    # Initialize Qdrant collection
    await qdrant_service.initialize_collection()
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Physical and Humanoid Robotics Book API",
    version="2.0.0",
    description="AI-Native robotics textbook with RAG-powered chat",
    lifespan=lifespan,
)

# Configure CORS for Docusaurus
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.v1 import chat, index

app.include_router(chat.router, prefix="/api/v1")
app.include_router(index.router, prefix="/api/v1")

# Health check
@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "features": ["RAG", "Chat", "Indexing"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
