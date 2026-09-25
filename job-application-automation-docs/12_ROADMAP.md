# Development Roadmap

## Phase 0: Documentation
- Requirements.
- Architecture.
- Data model.
- Security model.
- State machine.
- AI rules.
- Testing strategy.

## Phase 1: Candidate Profile
Build:
- Candidate profile UI.
- Education.
- Skills.
- Projects.
- Experience.
- Certifications.
- Resume upload/versioning.

## Phase 2: Job Import
Build:
- Generic connector interface.
- Manual URL import.
- Job parser.
- Normalized job schema.
- Deduplication.

Manual import should work before external connectors.

## Phase 3: Matching
Build:
- Requirement extraction.
- Skill normalization.
- Candidate evidence mapping.
- Explainable match output.

## Phase 4: Application Preparation
Build:
- Resume selection.
- Tailored summary.
- Cover letter.
- Question answering.
- Review interface.

## Phase 5: Tracking
Build:
- Application state machine.
- Timeline.
- Notes.
- Follow-up reminders.
- Search/filter dashboard.

## Phase 6: First permitted connector
Implement one source completely.

Do not implement many connectors before proving the architecture.

## Phase 7: Additional connectors
Add connectors individually.

## Phase 8: Submission assistance
Add permitted submission mechanisms with mandatory approval.

## Phase 9: Hardening
- Security review.
- Prompt injection tests.
- SSRF tests.
- Credential protection.
- Audit review.
- Duplicate submission testing.

## Phase 10: Deployment
Dockerize and deploy only after local end-to-end tests are reliable.
