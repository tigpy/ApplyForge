# Data Model

## Core entities

### Candidate
- id
- name
- email
- phone
- location
- profile_version
- created_at
- updated_at

### Education
- id
- candidate_id
- degree
- field
- institution
- start_date
- end_date
- status
- grade

### Skill
- id
- candidate_id
- name
- category
- proficiency
- evidence

### Project
- id
- candidate_id
- name
- description
- technologies
- url
- start_date
- end_date
- evidence

### Experience
- id
- candidate_id
- organization
- title
- type
- description
- start_date
- end_date
- evidence

### Certification
- id
- candidate_id
- name
- issuer
- status
- date
- credential_url

### Resume
- id
- candidate_id
- name
- job_family
- file_path
- version
- source
- created_at

### JobSource
- id
- name
- type
- configuration
- enabled

### Job
- id
- source_id
- external_id
- url
- title
- company
- location
- work_mode
- employment_type
- description_raw
- description_normalized
- discovered_at
- posted_at
- closing_at

Unique constraint:
```text
(source_id, external_id)
```

Fallback duplicate fingerprint:
```text
normalized_company + normalized_title + normalized_location
```

### JobRequirement
- id
- job_id
- requirement_type
- text
- normalized_skill
- mandatory
- evidence

### Match
- id
- job_id
- candidate_id
- match_version
- explanation
- hard_gaps
- strengths
- uncertainties
- created_at

### Application
- id
- candidate_id
- job_id
- resume_id
- status
- approved_at
- submitted_at
- external_application_id
- application_url
- notes

### ApplicationQuestion
- id
- application_id
- question
- answer
- answer_source
- requires_review
- final_answer

### AuditEvent
- id
- application_id
- event_type
- actor
- timestamp
- payload_hash
- metadata

## Important rule

Never store an AI-generated claim as a candidate fact without explicit user confirmation.
