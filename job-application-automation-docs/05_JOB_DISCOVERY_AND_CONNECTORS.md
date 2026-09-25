# Job Discovery and Connector Architecture

## Connector interface

Every connector should implement a common interface:

```python
class JobConnector:
    name: str

    def health_check(self) -> bool:
        ...

    def search(self, query, filters):
        ...

    def get_job(self, external_id):
        ...

    def normalize(self, raw_job):
        ...
```

If submission is supported and permitted:

```python
class ApplicationConnector(JobConnector):
    def prepare_application(self, application):
        ...

    def submit_application(self, application):
        ...
```

## Connector categories

1. Official APIs.
2. Public job feeds.
3. Public company career pages.
4. Permitted browser automation.
5. Manual-import connector.

Start with the least fragile mechanism.

## Connector rules

Each connector must document:
- Authentication method.
- Rate limits.
- Terms/usage restrictions.
- Supported operations.
- Fields available.
- Failure modes.
- Retry policy.
- Whether application submission is supported.
- Whether human interaction is required.

## Failure handling

```text
Request
  |
  +-- success -> normalize
  |
  +-- timeout -> retry with bounded backoff
  |
  +-- rate limited -> respect Retry-After / connector policy
  |
  +-- auth failure -> surface to user
  |
  +-- blocked/unsupported -> stop connector
```

Never attempt to bypass a platform control.

## Initial implementation strategy

Build a generic connector framework first.

Then implement one connector at a time and test it independently.

Do not create ten fragile connectors simultaneously.
