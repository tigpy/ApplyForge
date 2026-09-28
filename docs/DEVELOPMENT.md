# Development

- Backend: `cd backend && uvicorn app.main:app --reload`. Tables are created on startup (`init_db`); there are no migrations.
  To reset, delete `data/applyforge.db`.
- Frontend: `cd frontend && npm run dev`. API calls live only in `src/services/api.ts`.
- Add a job source: implement `JobConnector`, register it in `connectors/__init__.py`. Build a mock/fixture first.
- Add a real application flow: implement `ApplicationConnector` (or extend `BrowserAutomationService`). Test against a mock page
  before any real site. Confirm automated access is permitted by the site.
- Switch on real AI: set `OPENAI_API_KEY`. Every AI output is a Pydantic schema and is validated (score clamp, answer
  confidence >= 0.7, select options must match) before use.
- Test order: `pytest` -> `npm test` -> `npm run test:e2e`.
- Mock behaviours: URL containing `captcha` -> BLOCKED; URL containing `question` -> mandatory question that needs
  `work_authorization` in the profile facts.

## Verification status of this skeleton
Verified in the build environment: backend imports, SQLite init, FastAPI start, mock discovery/matching/apply, 28 pytest
tests, 4 Vitest tests, `npm run build`, Vite dev server + `/api` proxy.
NOT verified: the Playwright E2E test (Chromium could not be downloaded there), `OpenAIProvider` (needs a key),
`EmailNotificationService` (needs SMTP), `PlaywrightApplicationConnector` / `BrowserAutomationService` (no real site).
