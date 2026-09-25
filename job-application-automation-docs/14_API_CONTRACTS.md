# API Contract Outline

The API should be versioned:

```text
/api/v1
```

## Candidate

```text
GET    /candidate
PUT    /candidate
GET    /candidate/skills
POST   /candidate/skills
PATCH  /candidate/skills/{id}
DELETE /candidate/skills/{id}
```

## Resumes

```text
GET    /resumes
POST   /resumes
GET    /resumes/{id}
DELETE /resumes/{id}
```

## Jobs

```text
GET    /jobs
POST   /jobs/import
GET    /jobs/{id}
POST   /jobs/{id}/analyze
POST   /jobs/{id}/match
```

## Applications

```text
GET    /applications
POST   /applications
GET    /applications/{id}
PATCH  /applications/{id}
POST   /applications/{id}/prepare
POST   /applications/{id}/approve
POST   /applications/{id}/submit
```

The backend must reject submission unless the application is in an approved state.

## Audit

```text
GET /applications/{id}/audit
```

## API principles

- Validate all inputs.
- Use Pydantic schemas.
- Return stable error structures.
- Never expose secrets.
- Use authentication even in later single-user deployment if the UI is remotely accessible.
