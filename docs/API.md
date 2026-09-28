# API (base path `/api`, interactive docs at `/docs`)

Errors: `{"detail": "message"}` with a meaningful status (404, 409 invalid state, 413/415 bad upload, 422, 502).

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | status, active AI provider / connector / notifier |
| GET | `/resumes` | list |
| POST | `/resumes/upload` | multipart: `file` (PDF), optional `display_name`, `tags` (comma), `target_role` |
| DELETE | `/resumes/{id}` | 409 if an application references it |
| GET | `/jobs` | includes latest `match_score` |
| GET | `/jobs/{id}` | job + latest match |
| POST | `/jobs/discover` | body `{query?, connector?="mock"}`; idempotent |
| POST | `/jobs/{id}/match` | matches against all resumes; creates/refreshes the application (ELIGIBLE / SKIPPED / DUPLICATE) |
| GET | `/applications` | newest first |
| GET | `/applications/{id}` | includes `events` |
| POST | `/applications/{id}/apply` | runs synchronously; allowed from ELIGIBLE, FAILED, BLOCKED |
| GET / PUT | `/profile` | candidate profile incl. `facts` (verified extra answers) |
| POST | `/settings/test-email` | sends a test notification (mock unless SMTP configured) |

MatchResult: `{job_id, selected_resume_id, selected_resume_name, score, strengths, missing_requirements, reasons,
recommendation: APPLY|SKIP, resume_scores[], application_id, application_status}`.
