# Application State Machine

## States

```text
DISCOVERED
    |
    v
SAVED
    |
    v
ANALYZED
    |
    v
PREPARING
    |
    v
AWAITING_REVIEW
   / \
  /   \
SKIP  APPROVED
        |
        v
     SUBMITTING
      /      \
     /        \
SUBMITTED    FAILED
    |           |
    v           v
FOLLOW_UP    RETRY/REVIEW
    |
    +--> ASSESSMENT
    |
    +--> INTERVIEW
    |
    +--> REJECTED
    |
    +--> OFFER
    |
    +--> WITHDRAWN
```

## Transition rules

### DISCOVERED -> SAVED
User saves a job or an automated rule saves it.

### SAVED -> ANALYZED
Parser and matcher finish successfully.

### ANALYZED -> PREPARING
User requests application preparation.

### PREPARING -> AWAITING_REVIEW
Resume and answers are generated.

### AWAITING_REVIEW -> APPROVED
User explicitly approves submission.

### AWAITING_REVIEW -> SKIP
User rejects the application.

### APPROVED -> SUBMITTING
Submission process starts.

### SUBMITTING -> SUBMITTED
External platform confirms successful submission.

### SUBMITTING -> FAILED
Submission fails.

No state transition may silently skip human approval.

## Idempotency

Submitting the same application twice must be prevented where possible.

Before submission:
1. Check internal application history.
2. Check known external application ID.
3. Check source-specific duplicate indicators.
4. Require confirmation if duplicate status is uncertain.
