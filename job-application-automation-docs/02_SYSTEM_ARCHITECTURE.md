# System Architecture

## High-level architecture

```text
                    +----------------------+
                    |      Web UI          |
                    |       React          |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      FastAPI API     |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
       Candidate Service   Job Service    Application Service
              |                |                |
              +----------------+----------------+
                               |
                         PostgreSQL
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
       Background Worker                 File/Object Storage
       Celery/Redis                      resumes/exports
              |
      +-------+--------+
      |       |        |
      v       v        v
   Source   Parser    AI/LLM
 Connectors Pipeline  Services
```

## Recommended stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS if desired

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database
- PostgreSQL

### Background jobs
- Celery + Redis

### AI
Use an abstraction layer so the application is not coupled to one provider.

```text
LLMProvider
  -> ClaudeProvider
  -> LocalProvider
  -> FutureProvider
```

### Browser automation
Keep it isolated behind a connector interface. Use only where the target platform permits it.

## Architectural principles

1. API-first.
2. Connectors must be replaceable.
3. AI must not be the source of truth.
4. Candidate facts are immutable/source-controlled where possible.
5. Every application submission creates an audit record.
6. External platform failures must not corrupt internal state.
7. Imports must be idempotent.
8. Human approval is a state transition, not an informal UI action.

## Repository structure

```text
job-automation/
├── apps/
│   ├── api/
│   ├── worker/
│   └── web/
├── packages/
│   ├── domain/
│   ├── connectors/
│   ├── matching/
│   ├── llm/
│   ├── documents/
│   └── shared/
├── docs/
├── tests/
├── scripts/
├── docker/
├── .env.example
├── docker-compose.yml
└── README.md
```
