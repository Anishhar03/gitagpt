# Security

## Trust Boundaries

The browser is untrusted. FastAPI validates every schema, JWT, owner relationship, role, upload type, upload size, and document checksum. PostgreSQL and Redis should be reachable only from application networks. External model providers receive the retrieved passages, the user's question, and the optional conversation intention.

## Authentication and Authorization

- Development login must never be enabled on a public deployment.
- Production Google credentials are verified server-side against `GOOGLE_CLIENT_ID`.
- Application JWTs are signed with HS256 and a deployment secret; rotate the secret using a planned session invalidation or key-version strategy.
- Conversation, feedback, and bookmark reads include the authenticated user identity.
- Document writes require the `admin` role derived from `ADMIN_EMAILS`.

Google login proves identity, not organizational entitlement. Add hosted-domain or explicit allowlist checks in `verify_google_credential` when access must be restricted to an organization.

## Secrets

Keep secrets in the deployment platform's secret manager. Do not place them in `.env.example`, frontend build arguments, images, logs, screenshots, or repository URLs. Frontend variables beginning with `VITE_` are public by design.

Rotate a credential immediately if it appears in chat, shell history, an issue, or a commit. Removing it from the latest Git revision does not remove it from history. The repository verifier scans common GitHub, Google, and Groq credential patterns as a final guard, not as a substitute for secret scanning at the host.

## Uploads

The API accepts only `.pdf` filenames, `application/pdf` content type, the `%PDF` signature, and a configured maximum byte size. This does not prove that a complex PDF is harmless. For internet-facing administration, add malware scanning, decompression limits, parser isolation, and object-store quarantine before indexing.

Uploaded filenames are reduced to a safe basename, randomized, and never used as executable paths. Checksums reject duplicates. Serve originals only through an authenticated download endpoint if that feature is added.

## Web and Network Controls

- Terminate TLS at a trusted load balancer and redirect HTTP to HTTPS.
- Restrict CORS to exact production origins.
- Add CSP, HSTS, frame-ancestors, and MIME-sniffing headers at the edge.
- Keep PostgreSQL and Redis off public networks and require encrypted connections in production.
- Place rate limits at both the application identity layer and the edge IP layer.
- Protect `/metrics` with a private network or monitoring authentication.

## AI Safety and Privacy

Answers are constrained to retrieved text and persist their citations. The system prompt tells models not to invent verse numbers and not to act as medical, legal, financial, or crisis support. This is a product guardrail, not a proof of correctness.

Document which content is sent to Gemini or Groq, define retention expectations, and obtain appropriate user consent. Use local generation or an approved provider when organizational policy prohibits sending questions or source text to external services.

## Dependency and Release Hygiene

Pin critical packages, review automated update pull requests, generate an SBOM for released images, scan containers, and run images as non-root. CI has read-only repository permissions. Production releases should be built from reviewed commits and promoted by immutable image digest.
