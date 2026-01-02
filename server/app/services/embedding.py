"""
Jina AI embedding service for generating 1024-dim vectors.
Uses HTTP API directly to avoid dependency issues.
"""
import httpx
import asyncio
from typing import List
from app.core.config import settings


class JinaEmbeddingService:
    """Service for generating embeddings using Jina AI API."""

    def __init__(self):
        self.api_url = settings.JINA_API_URL
        self.api_key = settings.JINA_API_KEY
        self.model = settings.JINA_MODEL
        self.dimensions = settings.JINA_DIMENSIONS

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for the given text.

        Args:
            text: Input text to embed

        Returns:
            List of 1024 floats representing the embedding vector

        Raises:
            Exception: If API call fails after retries
        """
        return (await self.generate_embeddings([text]))[0]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with retry logic.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors

        Raises:
            Exception: If API call fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"model": self.model, "input": texts}

        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.api_url, json=payload, headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        return [item["embedding"] for item in data["data"]]

                    elif response.status_code == 429:
                        # Rate limit hit
                        delay = settings.RETRY_INITIAL_DELAY * (2**attempt)
                        print(
                            f"Rate limit hit. Retrying in {delay}s (attempt {attempt+1}/{settings.RETRY_ATTEMPTS})"
                        )
                        await asyncio.sleep(delay)
                    else:
                        raise Exception(
                            f"Jina API error: {response.status_code} - {response.text}"
                        )

            except httpx.TimeoutException:
                delay = settings.RETRY_INITIAL_DELAY * (2**attempt)
                print(
                    f"Request timeout. Retrying in {delay}s (attempt {attempt+1}/{settings.RETRY_ATTEMPTS})"
                )
                await asyncio.sleep(delay)

        raise Exception(
            f"Failed to generate embeddings after {settings.RETRY_ATTEMPTS} attempts"
        )


# Global service instance
jina_service = JinaEmbeddingService()
