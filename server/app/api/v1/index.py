"""
Indexing router for adding markdown content to the vector database.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from pydantic import BaseModel
from app.services.markdown_parser import markdown_parser
from app.services.embedding import jina_service
from app.services.vector_db import qdrant_service

router = APIRouter(prefix="/index", tags=["Indexing"])


class IndexRequest(BaseModel):
    """Request to index a specific chapter."""
    chapter_path: str
    chapter_id: str


class IndexResponse(BaseModel):
    """Response from indexing operation."""
    success: bool
    chunks_indexed: int
    chapter_id: str
    message: str


@router.post("/chapter", response_model=IndexResponse)
async def index_chapter(request: IndexRequest):
    """
    Index a single chapter into the vector database.

    Args:
        request: IndexRequest with chapter path and ID

    Returns:
        IndexResponse with status and chunk count
    """
    try:
        file_path = Path(request.chapter_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.chapter_path}")

        # Step 1: Parse markdown into chunks
        chunks = markdown_parser.parse_file(
            file_path=file_path,
            chapter_id=request.chapter_id,
            base_url="/docs",
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="No valid content found in file")

        # Step 2: Generate embeddings for all chunks
        texts = [chunk.text for chunk in chunks]
        embeddings = await jina_service.generate_embeddings(texts)

        # Assign embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk.vector = embedding

        # Step 3: Upsert to Qdrant
        success = await qdrant_service.upsert_chunks(chunks)

        if success:
            return IndexResponse(
                success=True,
                chunks_indexed=len(chunks),
                chapter_id=request.chapter_id,
                message=f"Successfully indexed {len(chunks)} chunks",
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to upsert chunks to Qdrant")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")


@router.post("/all")
async def index_all_chapters():
    """
    Index all chapters from the content/docs directory.

    Returns:
        Summary of indexing results
    """
    try:
        # Get the content/docs directory
        docs_dir = Path(__file__).parent.parent.parent.parent.parent / "content" / "docs"

        if not docs_dir.exists():
            raise HTTPException(status_code=404, detail="Docs directory not found")

        # Find all markdown files
        md_files = list(docs_dir.rglob("*.md"))

        if not md_files:
            raise HTTPException(status_code=404, detail="No markdown files found")

        results = []
        total_chunks = 0

        for md_file in md_files:
            # Skip intro.md and other special files
            if md_file.name in ["intro.md", "README.md"]:
                continue

            chapter_id = md_file.stem  # filename without extension

            # Parse and index
            chunks = markdown_parser.parse_file(
                file_path=md_file, chapter_id=chapter_id, base_url="/docs"
            )

            if chunks:
                # Generate embeddings
                texts = [chunk.text for chunk in chunks]
                embeddings = await jina_service.generate_embeddings(texts)

                for chunk, embedding in zip(chunks, embeddings):
                    chunk.vector = embedding

                # Upsert
                success = await qdrant_service.upsert_chunks(chunks)

                results.append({
                    "chapter": chapter_id,
                    "chunks": len(chunks),
                    "success": success,
                })

                total_chunks += len(chunks)

        return {
            "success": True,
            "total_chapters": len(results),
            "total_chunks": total_chunks,
            "details": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch indexing error: {str(e)}")


@router.delete("/chapter/{chapter_id}")
async def cleanup_chapter(chapter_id: str):
    """
    Remove all chunks for a deleted chapter.

    Args:
        chapter_id: Chapter slug to delete

    Returns:
        Success message
    """
    try:
        success = await qdrant_service.delete_by_chapter(chapter_id)

        if success:
            return {"success": True, "message": f"Deleted chapter: {chapter_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete chapter")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")
