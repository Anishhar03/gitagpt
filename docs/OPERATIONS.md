# Operations

## Signals

The API exports Prometheus data at `/metrics`:

- HTTP request count by method, path, and status.
- HTTP latency by method and path.
- Retrieval latency.
- Model requests by provider and outcome.

Structured JSON logs include request IDs. Preserve the incoming `X-Request-ID` at the edge or let the API create one, and return it in support tickets to correlate a user-visible failure.

Recommended dashboards cover request rate, p50/p95/p99 latency, 4xx/5xx rate, provider fallback rate, PostgreSQL pool saturation, Redis memory, RQ queue depth, oldest queued job age, ingestion duration, and document failure count.

## Alerts

Start with actionable alerts:

- Readiness fails for more than two minutes.
- API 5xx exceeds 2% for five minutes.
- p95 answer latency exceeds the chosen product objective.
- All hosted providers fail or local fallback use rises unexpectedly.
- Oldest ingestion job exceeds ten minutes.
- PostgreSQL disk, connection, or replica lag approaches its limit.
- Redis evictions occur outside expected cache keys.
- No successful backup has completed within the recovery policy.

## Backups

Back up PostgreSQL and uploaded PDFs. Redis is not the durable source of truth; restoring it is optional, but queued ingestion jobs may need to be re-enqueued. Periodically restore backups into an isolated environment and run the smoke test. A backup that has never been restored is only an assumption.

## Common Runbooks

### Knowledge base remains queued

1. Check `docker compose ps` or worker health in the orchestrator.
2. Inspect worker logs and RQ queue age.
3. Verify the API and worker use the same `REDIS_URL`, `DATABASE_URL`, and upload storage.
4. Restart a failed worker; the queued job remains in Redis.
5. For a failed document, inspect `error_message`, correct the input or service issue, delete it, and upload again.

### Answers return 503

Confirm at least one document is `ready`. A newly deployed stack intentionally refuses to answer without source context. If documents are ready, inspect PostgreSQL retrieval errors and the API request ID.

### Provider latency or outage

Inspect `model_requests_total` by provider and outcome. The chain should advance to Groq or local. Check external quotas and timeouts before raising worker counts; generation happens in API requests, not ingestion workers.

### High answer latency

Separate retrieval time from provider time. Check PostgreSQL query plans and HNSW index use, API saturation, model latency, and response size. Increase replicas only after identifying the constrained component.

### Redis unavailable

Readiness fails, rate limiting and daily cache are unavailable, and new ingestion jobs cannot queue. Durable conversations remain in PostgreSQL. Restore Redis, then verify queued/failed documents and re-enqueue as needed.

## Capacity

Measure before tuning. Important limits are API concurrency, PostgreSQL connections, vector index size, provider rate quota, Redis memory, worker throughput, PDF storage, and frontend/API egress. Configure API replicas so their total SQLAlchemy pools remain below the database connection budget; add PgBouncer when replica counts make that difficult.
