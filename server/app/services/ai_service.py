"""
Gemini AI service using OpenAI-compatible Agent SDK.
Handles RAG-enhanced chat responses with streaming support.
"""
import asyncio
from typing import List, Dict, AsyncGenerator
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from app.core.config import settings


class GeminiService:
    """Service for interacting with Gemini via OpenAI Agent SDK."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL
        )
        self.model = OpenAIChatCompletionsModel(
            openai_client=self.client, model=settings.LLM_MODEL
        )
        self.config = RunConfig(model=self.model, model_provider=self.client)
        print(f"✓ Using LLM: {settings.LLM_PROVIDER} ({settings.LLM_MODEL})")

    async def generate_response(
        self, query: str, context_chunks: List[Dict[str, any]]
    ) -> str:
        """
        Generate a response using Gemini with RAG context.

        Args:
            query: User's question
            context_chunks: Retrieved knowledge chunks from vector DB

        Returns:
            AI-generated response text

        Raises:
            Exception: If API call fails after retries
        """
        # Build context from retrieved chunks
        context_text = self._build_context(context_chunks)

        # Create system prompt with context
        system_prompt = f"""You are an expert robotics tutor helping students understand physical and humanoid robotics concepts.

Use the following context from the robotics textbook to answer the user's question. If the context doesn't contain relevant information, provide a general robotics answer but note it's not explicitly from the book.

Context:
{context_text}

Guidelines:
- Answer in clear, educational language
- Use SI units for all measurements
- Reference specific concepts from the context when applicable
- If mathematical formulas are involved, explain them step-by-step
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                # Use the OpenAI-compatible chat completion
                response = await self.client.chat.completions.create(
                    model=settings.LLM_MODEL, messages=messages, temperature=0.7
                )

                return response.choices[0].message.content

            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    delay = settings.RETRY_INITIAL_DELAY * (2**attempt)
                    print(
                        f"Rate limit/quota hit. Retrying in {delay}s (attempt {attempt+1})"
                    )
                    await asyncio.sleep(delay)
                elif "503" in str(e):
                    delay = settings.RETRY_INITIAL_DELAY * (2**attempt)
                    print(
                        f"Service unavailable. Retrying in {delay}s (attempt {attempt+1})"
                    )
                    await asyncio.sleep(delay)
                else:
                    raise Exception(f"Gemini API error: {e}")

        raise Exception(f"Failed to generate response after {settings.RETRY_ATTEMPTS} attempts")

    async def generate_response_stream(
        self, query: str, context_chunks: List[Dict[str, any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using Server-Sent Events.

        Args:
            query: User's question
            context_chunks: Retrieved knowledge chunks

        Yields:
            Response text chunks
        """
        context_text = self._build_context(context_chunks)

        system_prompt = f"""You are an expert robotics tutor helping students understand physical and humanoid robotics concepts.

Context from the textbook:
{context_text}

Answer the user's question using the context above. If the context doesn't contain relevant information, provide a general robotics answer with a disclaimer.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=settings.LLM_MODEL, messages=messages, temperature=0.7, stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"

    def _build_context(self, chunks: List[Dict[str, any]]) -> str:
        """Build formatted context string from retrieved chunks."""
        if not chunks:
            return "No relevant context found in the textbook."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']} - {chunk['chapter_id']}]\n{chunk['text']}\n"
            )

        return "\n\n".join(context_parts)


# Global service instance
gemini_service = GeminiService()
