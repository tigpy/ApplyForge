# ApplyForge

**ApplyForge** is an enterprise-grade, personal AI-assisted job discovery, application preparation, and career automation platform.

ApplyForge enforces **Zero Silent Submissions**—preparing materials, tailoring resumes, and extracting requirements automatically, while strictly requiring explicit human approval before any application is submitted.

---

## Target Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy 2.0, Alembic
- **Database**: PostgreSQL 16 + `pgvector`
- **Background Processing**: Celery, Redis
- **Browser Automation**: Playwright
- **AI Engine**: OpenAI API with Structured Outputs (Pydantic-grounded)
- **Document Processing**: ReportLab ATS PDF generator, PyMuPDF, python-docx, LaTeX → PDF
- **Observability & Logging**: Structured JSON logging, OpenTelemetry foundation
- **Infrastructure**: Docker Compose, Caddy reverse proxy, GitHub Actions CI
- **Deployment Target**: AWS

---

## Repository Structure

```
ApplyForge/
├── apps/
│   ├── web/                  # Next.js frontend with Tailwind CSS
│   └── api/                  # FastAPI backend with domain routers
├── workers/                  # Celery worker & background tasks
├── packages/
│   ├── ai/                   # OpenAI Structured Outputs integration
│   ├── automation/           # Playwright browser automation service
│   ├── connectors/           # Job discovery connectors (Manual, Mock, Public Feed)
│   ├── documents/            # Resume tailoring, ATS PDF & LaTeX generators, text extractors
│   ├── domain/               # SQLAlchemy models, Pydantic schemas, state machine
│   ├── matching/             # Deterministic requirement parser & explainable scoring
│   └── shared/               # Config, SSRF security auditor, JSON logger, telemetry
├── infrastructure/           # Caddyfile and deployment manifests
├── docker/                   # Dockerfiles for API, Worker, and Web
├── tests/                    # Pytest unit & integration test suite
├── alembic/                  # Database migration scripts
├── docker-compose.yml        # Multi-service local environment
└── .env.example              # Environment variables template
```

---

## Getting Started

### Option 1: Local Development (Fast & Simple)

1. **Install Python dependencies**:
   ```bash
   pip install -e .
   ```

2. **Initialize Database & Seed Verified Profile**:
   ```bash
   python scripts/seed_db.py
   ```

3. **Run Job Discovery**:
   ```bash
   python scripts/run_discovery.py mock
   # or for public remote feeds:
   python scripts/run_discovery.py public_feed
   ```

4. **Start the API Server**:
   ```bash
   python scripts/run_server.py
   ```
   Access the Career Desk at **http://localhost:8000/** and interactive API docs at **http://localhost:8000/docs**.

5. **Start Next.js Frontend (Optional)**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```
   Access Next.js at **http://localhost:3000/**.

---

### Option 2: Docker Compose

Start all services (PostgreSQL + pgvector, Redis, FastAPI, Celery worker, Next.js web, Caddy reverse proxy):

```bash
docker compose up --build
```

---

## Running Tests

Run the backend test suite:
```bash
python -m pytest -v
```

All 13 core safety, state machine, and API tests will run against an in-memory SQLite database without requiring external dependencies.
