# Research: Physical and Humanoid Robotics Book Foundation

## Decision: Decoupled Monorepo Structure
We will use a decoupled monorepo structure where the frontend (Docusaurus) and backend (FastAPI) live in separate top-level directories.

- **Rationale**: Keeps the codebase clean and allows independent deployments (e.g., Vercel for frontend, Render/Railway for backend). It aligns with the "Zero-Drift" folder structure defined in the Constitution.
- **Alternatives considered**:
    - Nested Backend: Putting FastAPI inside `frontend/api` (Rejected because it's less modular for RAG).
    - Single Project: Mixing Docusaurus and FastAPI files (Rejected as it violates the separation of concerns).

## Decision: uv for Python Management
We will use `uv` for all Python backend environment management.

- **Rationale**: `uv` is significantly faster than `pip` and provides better dependency resolution. It is explicitly mandated in the project Constitution.
- **Alternatives considered**:
    - `poetry`/`pipenv`: (Rejected as per Constitution constraint to use `uv`).

## Decision: JavaScript for Docusaurus
We will build the Docusaurus frontend using JavaScript (CommonJS/ESM).

- **Rationale**: Simplifies the integration of the "Urdu Translate" and "Personalize" buttons for AI agents. It reduces build-time complexity for these specialized features.
- **Alternatives considered**:
    - TypeScript: (Rejected as per Constitution constraint to use JavaScript).

## Decision: Modular FastAPI with APIRouter
The backend will use FastAPI's `APIRouter` to group functionally related endpoints.

- **Rationale**: Allows us to scale the RAG, Auth, and Personalization modules independently.
- **Implementation**:
    - `/routes/chat.py`: RAG logic.
    - `/routes/auth.py`: Better-Auth integration.
    - `/routes/personalize.py`: Personalization/Translation logic.

## Integration: Qdrant & Neon
- **Neon (Postgres)**: Primary store for user profiles, session data, and Better-Auth.
- **Qdrant (Vector DB)**: Vector store for book content embeddings to support context-aware search and chat.
