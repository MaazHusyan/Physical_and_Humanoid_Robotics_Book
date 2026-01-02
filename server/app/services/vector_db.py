"""
Qdrant vector database service for knowledge storage and retrieval.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import settings
from app.models.chat import KnowledgeChunk


class QdrantService:
    """Service for interacting with Qdrant Cloud."""

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self.dimensions = settings.JINA_DIMENSIONS

    async def initialize_collection(self):
        """
        Initialize the Qdrant collection if it doesn't exist.
        Creates collection with cosine similarity and 1024 dimensions.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimensions, distance=Distance.COSINE
                    ),
                )
                print(f"✓ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✓ Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            print(f"✗ Failed to initialize Qdrant collection: {e}")
            raise

    async def upsert_chunks(self, chunks: List[KnowledgeChunk]) -> bool:
        """
        Insert or update knowledge chunks in Qdrant.

        Args:
            chunks: List of KnowledgeChunk objects with embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            points = [
                PointStruct(
                    id=str(chunk.id),
                    vector=chunk.vector,
                    payload={
                        "text": chunk.text,
                        "chapter_id": chunk.chapter_id,
                        "title": chunk.title,
                        "source_url": chunk.source_url,
                    },
                )
                for chunk in chunks
                if chunk.vector is not None
            ]

            self.client.upsert(collection_name=self.collection_name, points=points)
            return True

        except Exception as e:
            print(f"✗ Failed to upsert chunks to Qdrant: {e}")
            return False

    async def search(
        self,
        query_vector: List[float],
        chapter_filter: Optional[str] = None,
        top_k: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_vector: Query embedding vector
            chapter_filter: Optional chapter ID to filter results
            top_k: Number of results to return

        Returns:
            List of matching chunks with metadata and scores
        """
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        query_filter = None
        if chapter_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="chapter_id", match=MatchValue(value=chapter_filter)
                    )
                ]
            )

        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=settings.SIMILARITY_THRESHOLD,
            ).points

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload["text"],
                    "chapter_id": result.payload["chapter_id"],
                    "title": result.payload["title"],
                    "source_url": result.payload["source_url"],
                }
                for result in results
            ]

        except Exception as e:
            print(f"✗ Qdrant search failed: {e}")
            return []

    async def delete_by_chapter(self, chapter_id: str) -> bool:
        """
        Delete all chunks for a specific chapter (cleanup for deleted files).

        Args:
            chapter_id: Chapter slug to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="chapter_id", match=MatchValue(value=chapter_id)
                        )
                    ]
                ),
            )
            return True
        except Exception as e:
            print(f"✗ Failed to delete chapter {chapter_id}: {e}")
            return False


# Global service instance
qdrant_service = QdrantService()
