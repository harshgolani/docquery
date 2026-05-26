# Docquery

RAG-powered PDF Q&A app. Upload a document, ask questions, get answers with source citations.

**Live Demo:** https://docquery-app.netlify.app

---

## How it works

1. Upload a PDF — text is extracted, chunked into 500-word segments, embedded via Voyage AI, and stored in ChromaDB
2. Ask a question — the question is embedded, top 4 matching chunks retrieved via vector search, passed to Claude Haiku as context
3. Get an answer with source citations — collapsible sources show exactly which chunks were used

## Stack

**Frontend:** React 19 + Vite → Netlify
**Backend:** FastAPI + ChromaDB + Voyage AI + Anthropic Claude → Render

## Architecture

Browser → Netlify (React) → Render (FastAPI)

The FastAPI backend calls three external services:
- Voyage AI — generates embeddings for chunks and questions
- ChromaDB — stores and retrieves vectors
- Anthropic Claude — generates answers from retrieved context

## Run locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY and VOYAGE_API_KEY
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /documents | List uploaded documents |
| POST | /upload | Upload a PDF |
| POST | /ask | Ask a question |
| DELETE | /document/{doc_id} | Delete a document |

## Design decisions

- **Voyage AI embeddings** over local sentence-transformers — API-based, no RAM overhead, deployable on Render free tier
- **ChromaDB PersistentClient** — document vectors survive server restarts
- **Filename stored in collection metadata** — document registry rebuilds correctly after restart
- **Session-based chat history** — in-memory only, no database required for Phase 1
- **10MB file size limit** — prevents oversized uploads crashing the free tier server

## Security

- CORS restricted to Netlify frontend URL
- 10MB file size limit on uploads
- 1000 character limit on questions
- Rate limiting: 5 uploads/hour and 20 questions/hour per IP
- API keys stored as environment variables, never in code
