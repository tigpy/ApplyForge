# Architecture

**Layers:** routers (validate, delegate) -> services (logic, no FastAPI) -> connectors / AI / DB.

## Key interfaces
| Interface | File | Implementations |
|---|---|---|
| `ResumeParser` | services/resume_service.py | `PyMuPDFResumeParser` |
| `ResumeRepository` | services/resume_service.py | DB-backed class |
| `ResumeMatcher` | services/matching_service.py | `HybridResumeMatcher` |
| `JobConnector` | connectors/base.py | `MockJobConnector` (register more in `connectors/__init__.py`) |
| `ApplicationConnector` | connectors/base.py | `MockApplicationConnector`, `PlaywrightApplicationConnector` |
| `AIProvider` | ai/client.py | `MockAIProvider`, `OpenAIProvider` |
| `NotificationService` | services/notification_service.py | `MockNotificationService`, `EmailNotificationService` |

`ApplicationConnector` is a *page driver* (open, detect_blocker, extract_fields, fill_field, upload_resume, submit).
`ApplicationService` decides what to fill, so blocker/unknown-field/confirmation rules live in one place for every site.

## Data model (SQLite)
`CandidateProfile` (single row) · `Resume` · `Job` (unique `source+external_id`, `fingerprint` for duplicates) ·
`MatchResult` (one row per match run) · `Application` (one per job) · `ApplicationEvent` (audit log).

## Matching
Per resume: deterministic score = share of required skills (from a shared vocabulary) found in the resume text;
AI score = semantic 0-100. Final = 0.7*deterministic + 0.3*AI. Best resume wins; `>= MATCH_THRESHOLD` -> APPLY.
Strengths/missing lists come only from deterministic evidence, never from AI output. If the AI call fails, the
deterministic score alone is used.

## States
DISCOVERED, MATCHED, ELIGIBLE, QUEUED, APPLYING, APPLIED, FAILED, SKIPPED, DUPLICATE, BLOCKED. Allowed transitions are
the `ALLOWED` table in `application_service.py` (FAILED/BLOCKED can be retried via QUEUED; APPLIED/DUPLICATE are terminal).
No approval gate.
