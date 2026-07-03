# Code Walkthrough

## Backend

`backend/app/main.py` composes middleware, routers, health instrumentation, static image delivery, and the startup seed. `config.py` centralizes environment settings. `database.py` owns the SQLAlchemy engine and transaction dependency.

`models.py` defines durable entities and ownership: users have conversations, conversations have messages, documents have vectorized chunks, and users attach feedback or bookmarks. The pgvector column uses JSON under SQLite so the same domain code runs in fast contract tests.

The router layer is intentionally thin:

- `routers/auth.py` exchanges development or Google identity for application JWTs.
- `routers/conversations.py` enforces ownership and coordinates retrieval, generation, persistence, feedback, streaming delivery, and export.
- `routers/knowledge.py` owns document administration, daily wisdom, and bookmarks.
- `routers/health.py` exposes infrastructure contracts.

Service modules isolate replaceable behavior. `embeddings.py` selects Gemini or deterministic embeddings. `retrieval.py` performs vector candidate selection and lexical reranking. `providers.py` implements the answer fallback chain. `ingestion.py` owns PDF extraction and indexing. `storage.py` is the boundary to replace when moving from a shared volume to object storage.

## Frontend

`frontend/src/App.jsx` coordinates authentication, React Query caches, navigation state, and mutations. `api.js` is the single HTTP boundary and normalizes errors. `AuthScreen.jsx`, `Sidebar.jsx`, `ChatView.jsx`, and `KnowledgeViews.jsx` divide the UI by workflow rather than by generic widget type.

Server data stays in React Query; only transient selection, drawer, composer, and notice state lives in components. The API origin is supplied at build time, while image URLs derive from that runtime client configuration. CSS establishes stable sidebar, header, message, composer, drawer, and mobile dimensions so dynamic content does not shift controls unexpectedly.

## Background Work

`seed.py` creates the bundled document once by checksum and queues its ID. `tasks.py` opens a fresh database session inside the worker process and delegates to ingestion. Queue payloads contain identifiers rather than ORM objects, keeping serialization stable and ensuring the worker reads current database state.

## Tests

Backend API tests use SQLite and a fake Redis implementation but traverse real FastAPI dependencies, SQLAlchemy models, retrieval, local generation, ownership, persistence, daily caching, and export. Service tests cover deterministic embeddings and chunking. Frontend tests run in jsdom. `scripts/smoke_test.py` is the final deployed-stack check against PostgreSQL, Redis, RQ, Nginx, and the API.

## Legacy Reference

`app.py` is the original Streamlit proof of concept. It is retained to show the evolution from one process and local Chroma to a multi-process platform. It is not imported by the new backend, built into the production image, or exercised by CI.
