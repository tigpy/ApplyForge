# Product Requirements Document

## 1. User

Primary user: one job seeker.

The architecture should allow future multi-user support, but v1 should not add unnecessary multi-tenancy complexity.

## 2. Functional requirements

### Candidate profile
- Store identity/contact information.
- Store education.
- Store skills with proficiency/evidence.
- Store projects.
- Store experience.
- Store certifications.
- Store links.
- Store work authorization/location preferences.
- Store job preferences.

### Resume management
- Upload master resume.
- Store resume versions.
- Associate resume versions with job families.
- Extract structured resume content.
- Preserve source-of-truth facts.
- Generate tailored drafts without changing factual claims.
- Export PDF when implemented.

### Job discovery
- Import jobs from permitted sources.
- Store source, URL, external ID, title, company, location, description, date discovered.
- Detect duplicates.
- Record connector provenance.

### Job analysis
Extract:
- Job title.
- Company.
- Location.
- Remote/hybrid/on-site.
- Employment type.
- Experience requirement.
- Education requirement.
- Required skills.
- Preferred skills.
- Responsibilities.
- Certifications.
- Work authorization/sponsorship language.
- Salary when available.
- Application URL.
- Closing date when available.

### Matching
Produce:
- Match explanation.
- Required-skill coverage.
- Preferred-skill coverage.
- Experience gap.
- Education compatibility.
- Location compatibility.
- Work-authorization uncertainty.
- Hard disqualifiers.
- Evidence supporting each positive match.

Do not produce a fake precision score if the underlying data is uncertain.

### Application preparation
Generate:
- Tailored resume selection/draft.
- Cover letter when useful.
- Answers to application questions.
- Short professional introduction.
- Recruiter message draft.

All generated claims must trace back to candidate facts.

### Human review
The user must be able to:
- Inspect job details.
- Inspect generated materials.
- Edit answers.
- Select/change resume.
- Approve.
- Reject.
- Save as draft.

### Submission
Only submit through:
- Official APIs where permitted.
- Supported application mechanisms.
- Browser automation only where permitted and technically appropriate.

Never bypass security or anti-automation controls.

### Tracking
Track:
- Discovered.
- Saved.
- Preparing.
- Awaiting review.
- Approved.
- Submitted.
- Assessment.
- Interview.
- Rejected.
- Withdrawn.
- Offer.
- Closed/Unknown.

## 3. Non-functional requirements

- Reliable retry handling.
- Idempotent imports.
- Auditability.
- Secrets stored securely.
- Structured logs.
- Database migrations.
- Automated tests.
- Docker-based local development.
- Clear connector boundaries.
- Failure recovery.
- Human-readable errors.
