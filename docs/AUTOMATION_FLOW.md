# Automation flow

```
POST /jobs/{id}/match          POST /applications/{id}/apply
 all resumes scored             duplicate check -> QUEUED -> (atomic claim) APPLYING
 best resume selected           open URL (validated) ............ event OPENED
 ELIGIBLE | SKIPPED | DUPLICATE detect blocker -> BLOCKED
                                extract fields ................. FIELDS_EXTRACTED
                                plan: profile data, else stored facts via AI, else "unknown"
                                any mandatory unknown -> BLOCKED (manual handling)
                                upload resume + fill ........... RESUME_SELECTED, FORM_FILLED
                                detect blocker again -> BLOCKED
                                submit ......................... SUBMITTED
                                site confirmed?  yes -> APPLIED -> notify (NOTIFIED)
                                                 no  -> FAILED ("not confirmed")
                                exception -> FAILED
```
## ATS Support & Connector Delegation (Phase 5)

When `APPLICATION_CONNECTOR=playwright`:
1. `PlaywrightApplicationConnector` opens the resolved application URL.
2. ATS Matcher check:
   - If URL or page HTML matches Greenhouse (`boards.greenhouse.io`, `#application_form`), delegates to `GreenhouseApplicationConnector`.
   - If URL or page HTML matches Lever (`jobs.lever.co`, `form[action*="lever.co"]`), delegates to `LeverApplicationConnector`.
   - Otherwise, falls back to generic browser form filling.
3. Form Sanity Check:
   - If the generic page contains no candidate inputs (e.g. it is just a job listing page with an un-followed "Apply" button or a search box), the application immediately fails fast with `BLOCKED` ("Unsupported application platform: <domain> (not an application form)").
4. Safe-Run Limits:
   - `MAX_APPLICATIONS_PER_RUN` (default: 10, configurable in `backend/.env`) bounds the number of applications submitted per batch. Any eligible jobs beyond the cap remain in their current state and are counted in `remaining`.
5. Public Feed Rate-Limiting:
   - `PublicFeedJobConnector` caches remote responses with a 30-second TTL and handles HTTP 429 backoff safely.

Rules: never bypass CAPTCHA/MFA/Cloudflare; never guess an answer; timeouts/unconfirmed submits are never APPLIED; FORM_FILLED logs
field labels only (no personal data); a notification failure never changes application status. Retrying a FAILED/BLOCKED
application goes through QUEUED again. In this skeleton apply runs inside the request; for slow real sites move it to
FastAPI `BackgroundTasks` and poll the application status.
