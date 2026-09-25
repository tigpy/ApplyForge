# How Claude Should Work On This Project

## Starting a task

Before editing:

```text
1. Identify requirement.
2. Read relevant docs.
3. Inspect existing code.
4. Identify dependencies.
5. State implementation plan internally.
6. Implement smallest complete change.
7. Test.
8. Report changed files and test results.
```

## Do not

- Generate a huge codebase in one response without validation.
- Replace working architecture because a different framework is fashionable.
- Add dependencies without reason.
- Create fake API integrations.
- Claim an external platform works without testing.
- Skip migrations.
- Skip tests because the feature appears simple.

## When an external platform is involved

First determine:
- Is an official API available?
- Is access permitted?
- What fields are available?
- What rate limits apply?
- Is application submission supported?
- Does the workflow require user interaction?

If those answers are unknown, implement the connector abstraction and a mock connector first.

## When AI is involved

Separate:

```text
LLM prompt
LLM response
validation
fact verification
user review
```

Never directly trust the raw LLM response.

## Progress format

After implementation, report:

```text
Implemented:
- ...

Files changed:
- ...

Tests:
- ...

Known limitations:
- ...

Next step:
- ...
```
