# Implementation Plan: Section 2 RAG Architecture

**Branch**: `002-section-intelligence-rag` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-section-intelligence-rag/spec.md`

## Summary

This plan outlines the technical architecture for the **Intelligence Layer** of the robotics book. We will implement a Retrieval-Augmented Generation (RAG) system using **FastAPI** on the backend. The core components include **Gemini 2.0 Flash** (via OpenAI-compatible SDK) for reasoning, **Jina AI** for generating high-quality robotics embeddings, and **Qdrant Cloud** for vector storage. The system will support real-time chat through Docusaurus and automated sidebar generation.

## Technical Context

**Language/Version**: Python 3.12 (via `uv`), JavaScript (Docusaurus)
**Primary Dependencies**: FastAPI, OpenAI SDK (for Gemini), Jina AI client, Qdrant Client, `python-dotenv`
**Storage**: Qdrant Cloud (Vector), Neon Serverless (Postgres for potential session data)
**Testing**: `pytest` for backend service logic, Docusaurus build check
**Target Platform**: Linux/Cloud
**Project Type**: Web Application (Decoupled Monorepo)
**Performance Goals**: < 1.5s Time to First Token (TTFT)
**Constraints**: < 200ms retrieval latency from Qdrant, SI units for all technical data
**Scale/Scope**: ~10 chapters initial, scalable to dozens of complex robotics modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **Section-Awareness**: Is this work limited to Section 2 (Intelligence/RAG)? **YES**
- [ ] **Tooling**: Is `uv` being used for Python management? **YES**
- [ ] **Coordination**: Are SI units and Z-up coordinates enforced for data? **YES**
- [ ] **SDD Flow**: Spec is complete and checklist generated. **YES**
- [ ] **Bonus Optimization**: Is RAG architected as a reusable Agent Skill? **YES**

## Project Structure

### Documentation (this feature)

```text
specs/002-section-intelligence-rag/
├── plan.md              # This file
├── research.md          # Phase 0: Gemini/Jina/Qdrant integration research
├── data-model.md        # Phase 1: Vector schema and Chat entities
├── quickstart.md        # Phase 1: Setup instructions for RAG
├── contracts/           # Phase 1: OpenAPI spec for /chat and /index
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
server/
├── main.py              # FastAPI Entry
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py      # Chat RAG endpoints
│   │       └── index.py     # Content indexing endpoints
│   ├── core/
│   │   ├── config.py    # Gemini/Qdrant settings
│   │   └── security.py
│   ├── services/
│   │   ├── ai_service.py   # Gemini/Agent SDK logic
│   │   ├── vector_db.py    # Qdrant client wrapper
│   │   └── embedding.py    # Jina AI logic
│   └── models/
│       └── chat.py         # Request/Response schemas
└── tests/

content/
├── docusaurus.config.js
├── sidebars.js          # Target for automation
└── docs/                # Knowledge source
```

**Structure Decision**: Decoupled monorepo with clean separation between `/server` (intelligence logic) and `/content` (UI/Docs).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
