# Changes

## 2.0.0 - Scalable platform

- Added a responsive React and Vite application for conversations, sources, bookmarks, and document administration.
- Added a versioned FastAPI API with JWT and Google OIDC-ready authentication.
- Added PostgreSQL persistence, pgvector retrieval, Alembic migrations, and hybrid reranking.
- Added Redis rate limiting, daily cache, and RQ background PDF ingestion.
- Added Gemini, Groq, and deterministic local provider fallback.
- Added structured logs, request IDs, readiness, Prometheus metrics, and non-root containers.
- Added backend coverage, frontend quality gates, secret verification, and a full Compose smoke test in GitHub Actions.
- Preserved the original Streamlit application as a legacy reference with isolated dependencies.

## 2026-05-27

- Rebuilt the Streamlit app into an end-to-end Gita RAG assistant powered by Gemini, LangChain, Chroma, and the local Bhagavad Gita PDF.
- Moved secret handling to environment variables and Streamlit Secrets; real API keys are intentionally excluded from Git.
- Added a polished landing experience, profile intake, chat flow, source passage viewer, and downloadable PDF transcript.
- Added deployment assets for Streamlit Cloud, Docker, and generic Python web hosts.
- Added developer documentation covering workflows, deployment, and the meaning of the major code blocks.
- Added lightweight project verification through `scripts/verify_project.py`.
- Removed generated vector-store data and local `.env` content from version control.
