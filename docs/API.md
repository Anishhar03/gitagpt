# API Contract

The OpenAPI document is available at `/docs` and `/openapi.json` while the API is running. Application routes use the `/api/v1` prefix; health and metrics routes are unversioned for infrastructure integrations.

## Authentication

Send the JWT returned by a login endpoint:

```http
Authorization: Bearer <access-token>
```

Development login is available only when `AUTH_MODE=development`:

```http
POST /api/v1/auth/dev
Content-Type: application/json

{"email":"admin@gitagpt.local","display_name":"Arjuna"}
```

For production, the browser obtains a Google Identity Services credential and submits it to `POST /api/v1/auth/google`. The API validates its audience against `GOOGLE_CLIENT_ID` before issuing an application JWT.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health/live` | Process liveness |
| `GET` | `/health/ready` | PostgreSQL and Redis readiness |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/api/v1/config` | Public runtime capabilities |
| `POST` | `/api/v1/auth/dev` | Development login |
| `POST` | `/api/v1/auth/google` | Google credential exchange |
| `GET` | `/api/v1/auth/me` | Current user |
| `GET/POST` | `/api/v1/conversations` | List or create conversations |
| `GET/PATCH/DELETE` | `/api/v1/conversations/{id}` | Read, edit, or archive owned conversation |
| `POST` | `/api/v1/conversations/{id}/messages` | Retrieve and answer a question |
| `POST` | `/api/v1/conversations/{id}/messages/stream` | SSE delivery of a completed answer |
| `POST` | `/api/v1/conversations/messages/{id}/feedback` | Upsert answer feedback |
| `GET` | `/api/v1/conversations/{id}/export` | Markdown transcript |
| `GET/POST` | `/api/v1/knowledge/documents` | List or upload PDFs |
| `DELETE` | `/api/v1/knowledge/documents/{id}` | Delete document and chunks |
| `GET` | `/api/v1/knowledge/daily` | Deterministic daily passage |
| `GET/POST` | `/api/v1/knowledge/bookmarks` | List or create bookmarks |
| `DELETE` | `/api/v1/knowledge/bookmarks/{id}` | Delete owned bookmark |

Document write endpoints require an administrator. All conversation, feedback, daily, and bookmark routes require authentication.

## Answer Example

```json
{
  "user_message": {"id": "...", "role": "user", "content": "How should I face uncertainty?"},
  "assistant_message": {
    "id": "...",
    "role": "assistant",
    "content": "### Reflection...",
    "provider": "local",
    "citations": [{"chunk_id": "...", "title": "Bhagavad Gita", "page_number": 18}],
    "latency_ms": 4
  },
  "sources": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "title": "Bhagavad Gita",
      "translation": "Bundled reference edition",
      "page_number": 18,
      "excerpt": "...",
      "score": 0.71
    }
  ]
}
```

## Status Codes

- `400`: invalid PDF signature or malformed request.
- `401`: missing, expired, or invalid token.
- `403`: authenticated user lacks administrator permission.
- `404`: resource does not exist or is not owned by the caller.
- `409`: duplicate document or bookmark.
- `413`: PDF exceeds the configured limit.
- `415`: upload is not a PDF.
- `422`: schema validation failed.
- `429`: per-user chat limit exceeded.
- `503`: dependencies are unavailable or the knowledge base is not ready.

Errors use FastAPI's standard `{"detail":"..."}` shape. Successful writes return persisted identifiers; clients should not generate authoritative IDs.
