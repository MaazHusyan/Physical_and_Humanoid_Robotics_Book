# Physical and Humanoid Robotics Book

An AI-native interactive textbook for learning physical and humanoid robotics concepts, powered by RAG (Retrieval-Augmented Generation).

## Overview

This project combines a Docusaurus-based frontend with a FastAPI backend to create an intelligent learning experience where students can ask questions and receive contextual answers from the textbook content.

## Features

### Section 1: Foundation ✅
- **Docusaurus Frontend**: Modern, responsive documentation site
- **Content Structure**: Organized chapters on robotics fundamentals
- **Auto-generated Sidebars**: Dynamic navigation from content structure
- **SI Units**: All measurements in meters, radians, kilograms

### Section 2: Intelligence Layer (RAG) ✅
- **FastAPI Backend**: High-performance async API server
- **Vector Database**: Qdrant Cloud for semantic search
- **Embeddings**: Jina AI v3 (1024 dimensions)
- **Multi-Provider LLM**:
  - Primary: Groq (Llama 3.3 70B) - 14,400 free requests/day
  - Backup: Gemini 2.0 Flash
- **RAG Pipeline**: Context-aware responses from textbook content
- **Streaming Support**: Server-Sent Events for real-time responses
- **Content Indexing**: Automatic markdown parsing and chunking

## API Endpoints

### Chat
- `POST /api/v1/chat/` - Standard chat with RAG context
- `POST /api/v1/chat/stream` - Streaming chat responses (SSE)

### Indexing
- `POST /api/v1/index/all` - Index all markdown content
- `POST /api/v1/index/chapter` - Index single chapter
- `DELETE /api/v1/index/chapter/{chapter_id}` - Remove chapter from index

### Health
- `GET /health` - Service health check
- `GET /docs` - Interactive API documentation

## Tech Stack

### Frontend
- Docusaurus 3.6.3
- React
- TypeScript (planned)

### Backend
- Python 3.12+ with uv package manager
- FastAPI with async support
- Qdrant Cloud (vector database)
- Jina AI (embeddings)
- Groq/Gemini (LLM via OpenAI SDK)
- Pydantic (data validation)

## Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- uv package manager
- Git

### Environment Variables

Create `/server/.env` with:

```env
# LLM Provider (groq or gemini)
LLM_PROVIDER=groq

# Groq API (https://console.groq.com)
GROQ_API_KEY=your_groq_key_here

# Gemini API (backup)
GEMINI_API_KEY=your_gemini_key_here

# Jina AI (https://jina.ai)
JINA_API_KEY=your_jina_key_here

# Qdrant Cloud (https://cloud.qdrant.io)
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_key_here

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Installation

**Backend:**
```bash
cd server
uv sync
uv run python main.py
```

**Frontend:**
```bash
cd content
npm install
npm start
```

## Current Status

- ✅ **Section 1**: Foundation complete
- ✅ **Section 2**: Intelligence layer complete
  - 39 knowledge chunks indexed from 9 chapters
  - RAG system fully operational
  - Streaming responses working
- ✅ **Section 3**: User authentication complete
  - User registration, login, and logout functionality
  - JWT-based authentication with refresh token rotation
  - Admin dashboard with user management
  - Session management and audit logging
- 🚧 **Section 4**: AI Features (in progress)
  - Docusaurus book with robotics content
  - RAG chatbot integration planned
  - Better-Auth integration preparation
  - Docker deployment for Hugging Face Spaces

## Project Structure

```
.
├── content/              # Docusaurus frontend
│   ├── docs/            # Robotics textbook content
│   │   ├── 01-introduction/
│   │   ├── 02-physical-fundamentals/
│   │   └── 03-humanoid-design/
│   └── src/             # React components
├── server/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API routes
│   │   ├── core/        # Configuration
│   │   ├── models/      # Pydantic models
│   │   └── services/    # Business logic
│   └── main.py          # Application entry
├── specs/               # Feature specifications
│   ├── 001-section-foundation/
│   └── 002-section-intelligence-rag/
└── history/             # Development history
    └── prompts/         # Prompt history records
```

## Development Approach

This project follows **Spec-Driven Development (SDD)** using SpecKit Plus:

1. **Specify** - Define feature requirements
2. **Plan** - Design architecture and approach
3. **Tasks** - Break down into actionable items
4. **Implement** - Execute tasks systematically
5. **Verify** - Test and validate

## Contributing

This is an educational project. Contributions should maintain:
- Clear documentation
- SI units throughout
- Test coverage for new features
- Adherence to the project constitution (`.specify/memory/constitution.md`)

## License

[Your License Here]

## Acknowledgments

Built with Claude Code and following Spec-Driven Development methodology.
