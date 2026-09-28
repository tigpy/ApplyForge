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
Rules: never bypass CAPTCHA/MFA; never guess an answer; timeouts/unconfirmed submits are never APPLIED; FORM_FILLED logs
field labels only (no personal data); a notification failure never changes application status. Retrying a FAILED/BLOCKED
application goes through QUEUED again. In this skeleton apply runs inside the request; for slow real sites move it to
FastAPI `BackgroundTasks` and poll the application status.
