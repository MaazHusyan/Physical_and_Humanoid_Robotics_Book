from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.services.vector_db import qdrant_service
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


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

# Configure SlowAPI for rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
from app.api.v1 import chat, index, auth, users, admin

app.include_router(chat.router, prefix="/api/v1")
app.include_router(index.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Health check
@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "features": ["RAG", "Chat", "Indexing"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
