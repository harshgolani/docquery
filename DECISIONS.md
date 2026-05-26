# Design Decisions

## Embeddings — Voyage AI over sentence-transformers

sentence-transformers loads an 80MB PyTorch model into RAM on startup. Render free tier has 512MB RAM total — not enough. Voyage AI is API-based, no local model, no RAM overhead. Switched to voyage-4-lite which has 200M free tokens on the free tier.

## ChromaDB — PersistentClient over EphemeralClient

Documents survive server restarts. On Render free tier, the server spins down after inactivity and restarts on next request. With EphemeralClient, users would lose all uploaded documents on every spin-down. PersistentClient writes to disk and survives restarts.

## Filename in ChromaDB metadata

The document registry (doc_id → filename mapping) is in-memory Python dict — lost on restart. ChromaDB collections persist but don't store application metadata by default. Storing filename in collection metadata at upload time allows the registry to rebuild correctly on startup via `_rebuild_registry()`.

## Session-based chat history

Chat history lives in React state only. Lost on page refresh. A production version would use PostgreSQL to persist conversations per user. For Phase 1 the use case is: upload → ask questions → done. No expectation of returning to previous conversations.

## 10MB file size limit

Render free tier has limited RAM. Large PDFs (100MB+) would exhaust memory during text extraction. 10MB covers most real-world documents (research papers, reports, contracts) while protecting the server.

## Question length limit (1000 chars)

Prevents unusually long inputs from consuming excess tokens in the Anthropic API call and adds a basic layer of input validation.

## CORS restricted to Netlify URL

Open CORS (`allow_origins=["*"]`) is fine for local development but exposes the API to any origin in production. Restricted to the Netlify frontend URL to prevent unauthorized cross-origin requests.

## UUID for doc_id

Guaranteed unique, no collision risk, no sanitization needed. Filename-based IDs would require handling duplicates, spaces, and special characters. ChromaDB collection names have character restrictions that UUIDs naturally satisfy.
