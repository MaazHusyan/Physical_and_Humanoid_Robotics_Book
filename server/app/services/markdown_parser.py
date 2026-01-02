"""
Markdown parser service for splitting content into knowledge chunks.
Splits by headers (H1, H2, H3) with max 1000 characters per chunk.
"""
import re
from typing import List, Tuple
from pathlib import Path
from app.models.chat import KnowledgeChunk
from app.core.config import settings


class MarkdownParser:
    """Service for parsing markdown files into knowledge chunks."""

    def __init__(self):
        self.max_chunk_size = settings.CHUNK_MAX_SIZE

    def parse_file(self, file_path: Path, chapter_id: str, base_url: str) -> List[KnowledgeChunk]:
        """
        Parse a markdown file into knowledge chunks.

        Args:
            file_path: Path to the markdown file
            chapter_id: Chapter slug (e.g., 'kinematics')
            base_url: Base URL for Docusaurus (e.g., '/docs')

        Returns:
            List of KnowledgeChunk objects (without embeddings)
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            return self.parse_content(content, chapter_id, base_url)
        except Exception as e:
            print(f"✗ Failed to parse {file_path}: {e}")
            return []

    def parse_content(self, content: str, chapter_id: str, base_url: str) -> List[KnowledgeChunk]:
        """
        Parse markdown content into knowledge chunks.

        Args:
            content: Markdown text content
            chapter_id: Chapter slug
            base_url: Base URL for Docusaurus

        Returns:
            List of KnowledgeChunk objects
        """
        chunks = []

        # Split by headers (H1, H2, H3)
        sections = self._split_by_headers(content)

        for title, text in sections:
            # Skip empty sections
            if not text.strip():
                continue

            # If section is too large, split further
            if len(text) > self.max_chunk_size:
                sub_chunks = self._split_large_section(text)
                for i, sub_text in enumerate(sub_chunks):
                    chunk = KnowledgeChunk(
                        text=sub_text,
                        chapter_id=chapter_id,
                        title=f"{title} (part {i+1})" if len(sub_chunks) > 1 else title,
                        source_url=f"{base_url}/{chapter_id}#{self._create_anchor(title)}",
                    )
                    chunks.append(chunk)
            else:
                chunk = KnowledgeChunk(
                    text=text,
                    chapter_id=chapter_id,
                    title=title,
                    source_url=f"{base_url}/{chapter_id}#{self._create_anchor(title)}",
                )
                chunks.append(chunk)

        return chunks

    def _split_by_headers(self, content: str) -> List[Tuple[str, str]]:
        """
        Split markdown content by headers.

        Returns:
            List of (title, text) tuples
        """
        # Pattern to match H1, H2, H3 headers
        header_pattern = r'^(#{1,3})\s+(.+)$'

        lines = content.split('\n')
        sections = []
        current_title = "Introduction"
        current_text = []

        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                # Save previous section
                if current_text:
                    sections.append((current_title, '\n'.join(current_text)))

                # Start new section
                current_title = match.group(2).strip()
                current_text = []
            else:
                current_text.append(line)

        # Add final section
        if current_text:
            sections.append((current_title, '\n'.join(current_text)))

        return sections

    def _split_large_section(self, text: str) -> List[str]:
        """
        Split a large section into smaller chunks while preserving sentence boundaries.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = ""

        # Split by sentences (rough approximation)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:self.max_chunk_size]]

    def _create_anchor(self, title: str) -> str:
        """
        Create a URL anchor from a title (Docusaurus style).

        Args:
            title: Header title

        Returns:
            URL-safe anchor string
        """
        return title.lower().replace(' ', '-').replace('/', '-')


# Global service instance
markdown_parser = MarkdownParser()
