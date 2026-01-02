# Data Model: Section 2 RAG

## Entities

### `KnowledgeCHUNK`
Represents a vectorized segment of the robotics book.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier for the chunk. |
| `vector` | Vector(1024) | 1024-dimension embedding (Jina v3). |
| `payload.text` | String | The actual markdown text content. |
| `payload.chapter_id` | String | Slug for the chapter (e.g., `kinematics`). |
| `payload.title` | String | The section title. |
| `payload.source_url` | String | URL to the Docusaurus page. |

### `ChatSession`
Represents a conversation between a student and the robotics agent.

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | UUID | Unique session identifier. |
| `messages` | List[Message] | History of chat turns. |
| `context_chunks` | List[UUID] | References to knowledge chunks used in this session. |

## Relationships
- **Chunk -> Chapter**: Many-to-one (indexed via payload).
- **Session -> Chunks**: Many-to-many (for traceability).

## Indexing Status
- **Collection Name**: `robotics_book_v1`
- **Distance Metric**: `Cosine`
- **Dimensionality**: `1024` (Jina v3 float)

---
> Generated with [Claude Code](https://claude.com/claude-code)
