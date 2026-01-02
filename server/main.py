from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, personalize

app = FastAPI(
    title="Physical and Humanoid Robotics Book API",
    version="1.0.0",
    description="Backend for the AI-Native robotics textbook"
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
app.include_router(chat.router, prefix="/api/v1")
app.include_router(personalize.router, prefix="/api/v1")

@app.get("/health", tags=["Status"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
