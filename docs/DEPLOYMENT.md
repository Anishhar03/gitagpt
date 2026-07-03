# Deployment

## Local Compose

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
python scripts/smoke_test.py
```

The stack exposes the web app on port `3000`, the API on `8000`, PostgreSQL on `5432`, and Redis on `6379`. The API runs Alembic before starting. Its lifespan queues the bundled PDF once by checksum, and the worker performs indexing.

Use `docker compose logs -f api worker` to watch startup and ingestion. Use `docker compose down -v` only when local database, queue, and uploads can be discarded.

## Production Shape

Build the root `Dockerfile` twice with different commands for API and worker. Build `frontend/Dockerfile` for the web image. Deploy PostgreSQL with the `vector` extension and Redis as managed stateful services where possible.

```text
Internet -> TLS/load balancer -> web CDN or Nginx
                             -> API replicas
API replicas -> PostgreSQL, Redis, Gemini/Groq
Worker replicas -> Redis, PostgreSQL, PDF storage
```

Run exactly one migration job for each release:

```bash
cd /app/backend
alembic -c alembic.ini upgrade head
```

Do not run migrations concurrently from every API replica in a larger deployment. The Compose entry point is convenient for one deployment unit; an orchestrator should use a dedicated pre-deploy migration task.

## Required Production Settings

```dotenv
ENVIRONMENT=production
AUTH_MODE=google
JWT_SECRET=<at-least-32-random-bytes>
GOOGLE_CLIENT_ID=<oauth-web-client-id>
ADMIN_EMAILS=owner@example.com
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=rediss://...
CORS_ORIGINS=https://gita.example.com
```

Set `GOOGLE_API_KEY`, `GROQ_API_KEY`, or both for hosted generation. Local fallback remains available, but production teams should decide whether that degraded behavior is preferable to returning an availability error.

`VITE_API_ORIGIN` is embedded during the frontend build:

```bash
docker build --build-arg VITE_API_ORIGIN=https://api.gita.example.com -t gita-gpt-web ./frontend
```

## Storage

The included implementation stores PDFs on a shared `/data/uploads` volume. This is correct for Compose and one-node deployments. Before running workers across multiple nodes, replace `services/storage.py` with object storage or mount a shared durable filesystem. Database backups do not contain the original PDF bytes.

## Health Checks

- `/health/live` verifies that the API process can serve requests.
- `/health/ready` verifies PostgreSQL and Redis connectivity.
- The web container serves `/` through Nginx.

Route traffic only to ready API instances. A worker does not expose HTTP; monitor RQ heartbeats and queue age instead.

## Release Verification

Every release should pass:

```bash
docker compose config --quiet
docker compose up -d --build
python scripts/smoke_test.py
```

The GitHub Actions workflow performs backend lint and coverage, frontend lint/test/build, then this container smoke test. A green unit test job alone does not prove PostgreSQL vector migration, Redis queueing, PDF ingestion, or browser bundle delivery.

## Rollback

1. Stop routing traffic to the new API image.
2. Restore the prior API, worker, and web image tags together.
3. Do not downgrade the database automatically. Review the migration's backward compatibility first.
4. Inspect failed jobs before requeueing; ingestion is checksum-idempotent but external model calls may not be.

Use expand-and-contract migrations for changes that span releases: add compatible schema, deploy code that understands both versions, backfill, then remove old schema in a later release.
