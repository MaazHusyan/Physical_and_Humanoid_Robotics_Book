# Data Model: Robotics Book Foundation

## Entity: User Profile
Stored in: **Neon (Postgres)** via Better-Auth extension.

- `id`: UUID (Primary Key)
- `email`: String (Unique)
- `software_background`: String (e.g., "Beginner", "Advanced")
- `hardware_background`: String (e.g., "None", "Engineer")
- `preferred_language`: String (default: "en", options: ["en", "ur"])

## Entity: Book Content (Chunk)
Stored in: **Qdrant (Vector Store)**

- `id`: UUID
- `vector`: Float[1536] (OpenAI embedding)
- `payload`:
    - `content`: String (The markdown text snippet)
    - `chapter_id`: String
    - `slug`: String
    - `metadata`: JSON (e.g., headers, context)

## Entity: Analytics/Interaction
Stored in: **Neon (Postgres)**

- `id`: UUID
- `user_id`: UUID (Foreign Key)
- `chapter_id`: String
- `interaction_type`: Enum ("read", "ask_chatbot", "personalize")
- `timestamp`: DateTime
