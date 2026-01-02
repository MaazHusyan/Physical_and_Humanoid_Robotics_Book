# Quickstart: Robotics Book Foundation

## Prerequisites
- Node.js (Latest LTS)
- Python 3.12+
- `uv` (Fast Python package manager)
- Git

## 1. Setup Backend
```bash
cd server
uv venv
source .venv/bin/activate
uv add fastapi uvicorn pydantic python-dotenv qdrant-client psycopg2-binary
```

## 2. Setup Frontend
```bash
cd content
npx create-docusaurus@latest . classic --javascript
npm install
```

## 3. Running the Project
- **Backend**: `uvicorn main:app --reload` (from `/server`)
- **Frontend**: `npm start` (from `/content`)

## 4. Environment Variables
Create a `.env` in the root with:
- `NEON_DATABASE_URL`
- `QDRANT_API_KEY`
- `QDRANT_URL`
- `OPENAI_API_KEY`
