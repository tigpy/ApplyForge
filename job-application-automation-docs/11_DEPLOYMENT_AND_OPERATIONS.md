# Deployment and Operations

## Development

Recommended local stack:

```text
React
FastAPI
PostgreSQL
Redis
Celery
```

Run through Docker Compose.

## Environments

```text
development
staging
production
```

Never use production credentials locally.

## Configuration

Use:

```text
.env
.env.example
```

`.env` must never be committed.

Example:

```env
DATABASE_URL=
REDIS_URL=
LLM_PROVIDER=
LLM_API_KEY=
ENCRYPTION_KEY=
```

## Observability

Provide:
- Structured application logs.
- Worker logs.
- Connector health.
- Failed job imports.
- Failed submissions.
- Queue status.

## Backups

Back up:
- PostgreSQL database.
- Candidate profile.
- Application records.
- Generated document metadata.

Do not blindly back up temporary browser sessions.

## Recovery

If a worker crashes:
- Job remains retryable.
- State does not incorrectly become successful.
- Duplicate processing is prevented through idempotency keys.
