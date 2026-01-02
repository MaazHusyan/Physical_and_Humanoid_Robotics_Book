# API Contract: Robotics Book Foundation

## Backend Base URL: `/api/v1`

### 1. Health and Status
- **GET `/health`**
  - **Description**: Returns server status.
  - **Response**: `{ "status": "healthy", "version": "1.0.0" }`

### 2. Chat/RAG (Placeholder)
- **POST `/chat`**
  - **Description**: Send a message to the AI chatbot.
  - **Request**: `{ "message": "What is ZMP?", "context": "optional_selected_text" }`
  - **Response**: `{ "answer": "...", "sources": [...] }`

### 3. Personalization (Placeholder)
- **POST `/personalize`**
  - **Description**: Adjust chapter content based on user profile.
  - **Request**: `{ "user_id": "...", "chapter_id": "..." }`
  - **Response**: `{ "personalized_content": "..." }`

### 4. Translation (Placeholder)
- **POST `/translate`**
  - **Description**: Get Urdu translation for a specific chapter section.
  - **Request**: `{ "content": "..." }`
  - **Response**: `{ "translated_text": "..." }`
