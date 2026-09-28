# ApplyForge 🚀
> **Personal Job-Search & Automated Application Engine**  
> ApplyForge automatically indexes your resumes, discovers jobs, matches each role across all your resumes, selects the best resume, and applies autonomously using verified candidate information with real browser automation.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Tests-Pytest%20%7C%20Vitest%20%7C%20E2E-success)](https://pytest.org)

---

## ⚡ Overview

ApplyForge is designed to remove the repetitive friction of job applications. Instead of manually uploading PDFs, copy-pasting candidate facts, and filling repetitive fields on career portals, ApplyForge runs an end-to-end autonomous pipeline:

```
Upload Multiple Real Resumes
          ↓
Configure Job Preferences & Exclusions
          ↓
Discover Jobs (Mock / Public Feed)
          ↓
Match Every Job Against ALL Resumes
          ↓
Select Highest-Scoring Deterministic Resume
          ↓
Automate Application via Playwright Browser
          ↓
Verify Actual Confirmation & Save Audit Record
          ↓
Send Instant Notification (Success or Blocker)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 React + TypeScript Frontend                 │
│    Dashboard · Resume Manager · Jobs · Applications · Config │
└──────────────────────────────┬──────────────────────────────┘
                               │ /api
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Python Backend                   │
│   Routers (Resumes, Jobs, Automation, Profile, Application) │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
│  Services   │         │ Match Engine│         │ Connectors  │
│  · Resume   │         │ · Overlap   │         │ · Mock      │
│  · Job      │         │ · Semantics │         │ · Public    │
│  · Auto-App │         │ · Ranking   │         │ · Playwright│
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
┌──────▼───────────────────────▼───────────────────────▼──────┐
│                      SQLite / SQLAlchemy                    │
│   Resumes · CandidateProfile · Jobs · Events · Audit Trail  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **Multi-Resume Management**: Upload real PDF resumes (e.g. Cybersecurity, SOC Analyst, Backend Developer, Java, General). Original PDFs are preserved byte-for-byte, extractable text is indexed, and duplicate file uploads are prevented.
- **Job Preferences System**: Set target roles, preferred locations (e.g. Mumbai, Remote, India), remote/hybrid/onsite workplace preferences, minimum experience, and company/role exclusions.
- **Deterministic Multi-Resume Matching**: Evaluates every discovered job against *all* uploaded resumes. Calculates deterministic skill overlap, ranks all candidates, and links the highest scoring resume to the application.
- **One-Click Automation ("Run Job Search")**: One action discovers jobs, de-duplicates them, matches against all resumes, selects winning resumes, applies via headless Playwright, records events, and sends notifications.
- **Real Playwright Browser Automation**: Generic, robust browser automation that opens application portals, extracts fields, maps verified candidate data, uploads the winning PDF, clicks submit, and only confirms when genuine confirmation text appears on the page.
- **Safety First & Anti-Hallucination**:
  - Never invents candidate facts or answers.
  - Unknown mandatory questions mark the application as `REQUIRES_MANUAL_ACTION` instead of guessing.
  - CAPTCHA and bot verification cleanly mark applications as `BLOCKED`.
  - Atomic database claims ensure no job is ever applied to twice.
- **Notifications**: Instant notifications via structured mock event logs or real SMTP email on both successful applications and blocked attempts.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # On Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
python -m playwright install chromium

# Copy environment configuration
cp .env.example .env

# Run FastAPI backend
uvicorn app.main:app --reload --port 8000
```
- API server runs at: `http://127.0.0.1:8000`
- Interactive OpenAPI docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

```bash
# In a second terminal
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
- Web UI is live at: `http://localhost:5173`

### 3. Generate Sample Resumes

To quickly populate sample resumes for local development:
```bash
python scripts/make_sample_resumes.py
```
This generates 5 distinct resumes in `resumes/` and `data/sample-resumes/`:
1. `cybersecurity.pdf` (Cybersecurity Analyst)
2. `soc-analyst.pdf` (SOC Analyst)
3. `backend-developer.pdf` (Backend Python Developer)
4. `java-developer.pdf` (Java Backend Developer)
5. `fresher-general.pdf` (Junior Software Developer)

---

## 🧪 Testing

ApplyForge features complete test suites across unit, integration, and browser levels:

```bash
# 1. Run all backend tests (Pytest - 32 tests including real Playwright browser automation)
cd backend
python -m pytest

# 2. Run frontend unit/component tests (Vitest)
cd frontend
npm test

# 3. Run Playwright mock workflow E2E test
cd frontend
npm run test:e2e
```

---

## 🔒 Configuration (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API Key (leave empty for deterministic mock AI) | `""` |
| `OPENAI_MODEL` | OpenAI Model | `gpt-4o-mini` |
| `AI_PROVIDER` | `auto`, `openai`, or `mock` | `auto` |
| `SMTP_HOST` | SMTP server host for email notifications | `""` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP account username | `""` |
| `SMTP_PASSWORD` | SMTP account password | `""` |
| `NOTIFICATION_EMAIL` | Destination email address for notifications | `""` |
| `NOTIFICATION_MODE` | `auto`, `email`, or `mock` | `auto` |
| `DATABASE_URL` | SQLite database URI | `sqlite:///./data/applyforge.db` |
| `RESUME_DIR` | Directory to store uploaded resume PDFs | `./resumes` |
| `APPLICATION_CONNECTOR` | `mock` or `playwright` | `mock` |
| `BROWSER_HEADLESS` | Run Playwright in headless mode | `true` |
| `MATCH_THRESHOLD` | Minimum score percentage to mark application ELIGIBLE | `75` |
| `ALLOW_LOCAL_URLS` | Allow local URLs for test application servers | `false` |
| `CORS_ORIGINS` | Permitted frontend origins | `http://localhost:5173` |

---

## 🛡️ Safety & Ethics Model

1. **Deterministic Accuracy**: Candidate credentials, work experience, and educational background are never fabricated or embellished.
2. **Verified Facts Only**: Answers to mandatory form questions are sourced strictly from the user's verified candidate profile and stored facts.
3. **Graceful Escalation**: If an application requires manual input (CAPTCHA, unknown mandatory questions, MFA), it transitions to `BLOCKED` or `REQUIRES_MANUAL_ACTION`.
4. **Idempotent Submissions**: Fingerprint hashing and atomic database claims prevent duplicate submissions to identical roles.
5. **PII Sanitization**: Sensitive candidate data is excluded from application audit logs and browser event summaries.

---

## 📄 License

MIT License. Built for personal job search automation.
