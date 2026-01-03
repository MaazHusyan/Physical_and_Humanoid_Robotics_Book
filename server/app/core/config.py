"""
Configuration module for loading environment variables.
Handles API keys for Gemini, Jina AI, and Qdrant Cloud.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # LLM Configuration (Groq or Gemini)
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "gemini"

        # Groq Configuration (Recommended - Free & Fast)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GROQ_BASE_URL = "https://api.groq.com/openai/v1"
        self.GROQ_MODEL = "llama-3.3-70b-versatile"  # or "llama-3.1-70b-versatile"

        # Gemini Configuration (Backup)
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.GEMINI_MODEL = "gemini-2.0-flash-exp"

        # Active LLM settings (auto-selected based on LLM_PROVIDER)
        self.LLM_API_KEY = self.GROQ_API_KEY if self.LLM_PROVIDER == "groq" else self.GEMINI_API_KEY
        self.LLM_BASE_URL = self.GROQ_BASE_URL if self.LLM_PROVIDER == "groq" else self.GEMINI_BASE_URL
        self.LLM_MODEL = self.GROQ_MODEL if self.LLM_PROVIDER == "groq" else self.GEMINI_MODEL

        # Jina AI Configuration
        self.JINA_API_KEY = os.getenv("JINA_API_KEY", "")
        self.JINA_API_URL = "https://api.jina.ai/v1/embeddings"
        self.JINA_MODEL = "jina-embeddings-v3"
        self.JINA_DIMENSIONS = 1024

        # Qdrant Configuration
        self.QDRANT_URL = os.getenv("QDRANT_URL", "")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
        self.QDRANT_COLLECTION = "robotics_book_v1"
        self.QDRANT_DISTANCE_METRIC = "Cosine"

        # Application Settings
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/robotics_book")

        # RAG Settings
        self.CHUNK_MAX_SIZE = 1000
        self.RETRIEVAL_TOP_K = 3
        self.SIMILARITY_THRESHOLD = 0.7
        self.RETRY_ATTEMPTS = 3
        self.RETRY_INITIAL_DELAY = 2.0

        # Authentication Settings
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    def validate(self) -> bool:
        """Validate that required API keys are set."""
        required = {
            "JINA_API_KEY": self.JINA_API_KEY,
            "QDRANT_URL": self.QDRANT_URL,
            "QDRANT_API_KEY": self.QDRANT_API_KEY,
        }

        # Validate LLM provider has required key
        if self.LLM_PROVIDER == "groq":
            required["GROQ_API_KEY"] = self.GROQ_API_KEY
        else:
            required["GEMINI_API_KEY"] = self.GEMINI_API_KEY

        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True


# Global settings instance
settings = Settings()
