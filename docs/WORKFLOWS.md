# Workflows

## First Startup

1. PostgreSQL and Redis become healthy.
2. The API runs Alembic and starts serving readiness.
3. The bundled PDF is copied to durable upload storage and inserted once by checksum.
4. Its document ID is queued in Redis.
5. The worker extracts pages, creates overlapping chunks, embeds them, and marks the document ready.
6. The web app shows readiness through the administrator document view.

## Conversation

1. The user signs in and creates or selects a conversation.
2. The API verifies JWT identity and ownership.
3. Redis enforces the per-user one-minute rate window.
4. Hybrid retrieval selects source passages from ready documents.
5. The prompt labels each source and includes the user's stated intention.
6. Gemini, Groq, or local generation returns a structured reflection.
7. The question, answer, provider, latency, and citations commit together.
8. The UI renders Markdown, opens source passages, and accepts feedback or bookmarks.

## Document Administration

1. An administrator submits title, translation, and PDF.
2. The API validates role, type, signature, size, filename, and checksum.
3. The committed document appears as queued.
4. The worker changes it to processing and then ready or failed.
5. Deleting a document removes its chunks and stored file. Historical assistant messages retain citation snapshots but their bookmark targets are removed with the chunks.

## Degraded Modes

- No model keys: local grounded generation remains functional.
- Gemini failure: Groq is attempted when configured, then local.
- No ready documents: answers return 503 instead of fabricating context.
- Redis failure: readiness fails; durable content remains intact.
- Worker failure: chat over already indexed content remains available; new documents remain queued.
- Web failure: API remains independently observable and restartable.

## Continuous Integration

Backend and frontend quality jobs run in parallel. The container job begins only after both pass, builds every image, migrates a real pgvector database, indexes the bundled PDF through Redis and RQ, and exercises the public contracts through HTTP.
