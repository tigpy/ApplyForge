# ApplyForge

Personal job-application automation. You provide existing resume PDFs; ApplyForge:

1. reads and indexes them, 2. discovers jobs, 3. extracts requirements, 4. scores the job against **every** resume,
5. picks the best resume and decides whether to apply, 6. opens the application and fills it from verified data,
7. submits automatically, 8. records exactly what happened, 9. notifies you.

```
Applied Successfully
Company: Example Corp | Role: Junior Security Analyst | Resume used: cybersecurity.pdf | Match: 91% | Status: Applied
```

**Status:** working skeleton. Everything runs end to end on **mock** connectors. No real job board or real application
site is integrated; `PlaywrightApplicationConnector` is a generic, *unverified* implementation.

## Stack
React + TypeScript + Vite + Tailwind (frontend) · Python + FastAPI + Pydantic + SQLAlchemy + SQLite (backend) ·
OpenAI API with structured outputs (mock provider by default) · Playwright · PyMuPDF · SMTP · Pytest, Vitest, Playwright tests.

## Architecture
```
Frontend (React) --/api--> FastAPI routers --> services --> connectors (mock | playwright)
                                                  |--> ai (OpenAIProvider | MockAIProvider)
                                                  |--> SQLite (SQLAlchemy)
                                                  '--> notifications (email | mock)
```
Routers are thin. All logic is in `services/`. Browser code exists only in `services/browser_service.py`.
Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Folder structure
```
backend/app/{main,config,database,security,skills,presenters}.py
backend/app/models/      SQLAlchemy tables + status enum
backend/app/schemas/     Pydantic request/response models
backend/app/routers/     /api endpoints
backend/app/services/    resume, job, matching, application, notification, browser
backend/app/ai/          AIProvider, OpenAI + mock, matching & answer schemas
backend/app/connectors/  JobConnector / ApplicationConnector + mock + playwright
backend/tests/           pytest
frontend/src/            pages, components, services (API client), hooks, types
frontend/e2e/            Playwright mock end-to-end test
resumes/  data/          your PDFs and the SQLite DB (git-ignored)
scripts/                 make_sample_resumes.py
```

## Features & Workflow
- **Multi-Resume Management**: Upload, preview extracted text, and manage multiple PDF resumes. Prevents duplicate uploads.
- **Job Preferences**: Set target roles, preferred locations, workplace preference (remote/hybrid/onsite), minimum experience, and company/role exclusions.
- **Connectors**:
  - `mock`: Completely reliable offline mock discovery & application testing.
  - `public_feed`: Discovers public tech jobs with built-in offline snapshot fallback.
  - `playwright`: Real browser automation with form inspection, input filling, resume uploading, and confirmation verification.
- **Deterministic Multi-Resume Matching**: Evaluates jobs against every uploaded resume and selects the highest scoring resume.
- **One-Click Automation ("Run Job Search")**: Discovers jobs -> matches against all resumes -> ranks opportunities -> selects best resumes -> applies automatically -> saves audit record -> sends notifications.
- **Safety Protections**: Never invents candidate facts; unknown mandatory fields transition to `REQUIRES_MANUAL_ACTION`; CAPTCHA blocks application cleanly; never applies twice.

## Setup & Running

### Backend
```bash
cd backend
# Optional: create & activate virtualenv
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium   # once for Playwright browser automation
uvicorn app.main:app --reload           # runs on http://127.0.0.1:8000 (docs at /docs)
```

### Frontend
```bash
cd frontend
npm install
npm run dev                             # runs on http://localhost:5173 (proxies /api to :8000)
```

Sample resumes for trying it out: `python scripts/make_sample_resumes.py` (generates sample resumes in `resumes/` and `data/sample-resumes/`).
Open the Dashboard at `http://localhost:5173` and click **Run Job Search**!

## Environment variables (`backend/.env`)
| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY`, `OPENAI_MODEL` | real AI; empty key = mock AI | mock / `gpt-4o-mini` |
| `AI_PROVIDER` | `auto`, `openai`, `mock` | `auto` |
| `SMTP_HOST/PORT/USERNAME/PASSWORD`, `NOTIFICATION_EMAIL` | email notifications | empty = mock notifier |
| `NOTIFICATION_MODE` | `auto`, `email`, `mock` | `auto` |
| `DATABASE_URL` | SQLite URL (relative paths resolve from repo root) | `sqlite:///./data/applyforge.db` |
| `RESUME_DIR` | where uploaded PDFs are stored | `./resumes` |
| `APPLICATION_CONNECTOR` | `mock` or `playwright` | `mock` |
| `MATCH_THRESHOLD` | score needed to be ELIGIBLE | `75` |
| `MAX_UPLOAD_MB`, `BROWSER_HEADLESS`, `CORS_ORIGINS` | misc | `5`, `true`, `http://localhost:5173` |

## Tests
```bash
cd backend && source .venv/bin/activate && python -m pytest          # backend
cd frontend && npm test                                              # Vitest
cd frontend && npx playwright install chromium                       # once
cd frontend && npm run test:e2e                                      # mock E2E (backend venv must be active)
```

## How the automation flow works
Job -> Match (all resumes) -> select resume -> ELIGIBLE -> open application URL -> extract form fields -> map stored
candidate data -> upload resume -> fill -> submit -> record -> notify. Unknown mandatory fields, CAPTCHA/MFA and
unconfirmed submissions **never** become APPLIED. See [docs/AUTOMATION_FLOW.md](docs/AUTOMATION_FLOW.md).

## Safety rules (enforced in code)
Secrets only via env vars, `.env` git-ignored · PDF-only, size-limited, sanitized uploads · external URLs validated
(no localhost/private ranges) before browsing · AI answers only from stored facts, else BLOCKED · CAPTCHA/MFA is never
bypassed · APPLIED only after the site confirms · one application per job, atomic claim prevents double submission.
