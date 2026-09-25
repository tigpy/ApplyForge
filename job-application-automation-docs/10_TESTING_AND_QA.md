# Testing and Quality Assurance

## Test layers

### Unit tests
Test:
- Parsers.
- Normalizers.
- Matchers.
- State transitions.
- Deduplication.
- Validation.

### Integration tests
Test:
- API + database.
- Worker + queue.
- Connector + mock source.
- Document generation.

### End-to-end tests
Test:

```text
Import job
 -> parse
 -> match
 -> prepare
 -> review
 -> approve
 -> submit mock
 -> track
```

## Critical safety tests

The system must fail tests if:
- Submission occurs without approval.
- Unknown facts are presented as facts.
- Duplicate application is submitted.
- Credentials appear in logs.
- External job text is executed as instructions.
- A failed submission is marked successful.
- AI output overwrites candidate facts.

## Connector testing

Never run destructive tests against a real application form.

Use:
- Mock servers.
- Sandbox environments.
- Recorded fixtures.
- Local test pages.

## Acceptance criteria

A feature is not complete until:
- Tests pass.
- Error handling exists.
- Audit logging exists where relevant.
- Documentation exists.
- Failure behavior is defined.
