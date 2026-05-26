# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Docquery is a RAG (Retrieval-Augmented Generation) app with two independent services:

- **`backend/`** — Python/FastAPI server that handles PDF ingestion and Q&A
- **`frontend/`** — React 19 + Vite SPA (currently a scaffold; the real UI connecting to the backend is yet to be built)

### Backend data flow

1. `POST /upload` — accepts a PDF, extracts text via `pypdf`, splits into 500-word overlapping chunks, embeds with `sentence-transformers` (`all-MiniLM-L6-v2`), and stores in ChromaDB. Each document gets its own ChromaDB collection named by its UUID `doc_id`.
2. `POST /ask` — embeds the question, runs a similarity query against the document's ChromaDB collection (top-4 chunks), then sends context + question to Claude (`claude-haiku-4-5`) and returns the answer with source chunks.
3. `GET /documents` — returns the in-memory `document_registry` (does **not** persist across server restarts — uploaded docs are re-queryable via ChromaDB but won't appear in the list after a restart).
4. `DELETE /document/{doc_id}` — deletes the ChromaDB collection and removes from the in-memory registry.

ChromaDB data is persisted on disk at `backend/chroma_db/`.

## Commands

### Backend

```bash
cd backend
pip install -r requirements.txt        # first-time setup
cp .env.example .env                   # then add ANTHROPIC_API_KEY
uvicorn main:app --reload              # runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install                            # first-time setup
npm run dev                            # runs on http://localhost:5173
npm run build                          # production build
npm run lint                           # ESLint check
npm run preview                        # preview production build locally
```

## Key constraints

- `document_registry` is in-memory only — document metadata is lost on backend restart even though the ChromaDB vectors remain on disk.
- CORS is open (`allow_origins=["*"]`); restrict before any public deployment.
- Only PDF uploads are supported; the `/upload` endpoint rejects non-`.pdf` filenames.
- The frontend (`src/App.jsx`) is still the default Vite scaffold — it does not yet call any backend endpoints.
