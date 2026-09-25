# Job Matching Engine

## Goal

Help the user understand whether a job is relevant and what evidence supports that conclusion.

## Pipeline

```text
Raw Job
  |
  v
Normalize text
  |
  v
Extract requirements
  |
  v
Normalize skills/entities
  |
  v
Compare candidate profile
  |
  +--> Required skills
  +--> Preferred skills
  +--> Experience
  +--> Education
  +--> Location
  +--> Work authorization
  +--> Certifications
  |
  v
Generate explanation
```

## Matching categories

### Strong evidence
Candidate explicitly has the skill or experience.

### Transferable
Candidate has closely related experience but not the exact wording.

### Missing
Requirement is explicitly absent from the candidate profile.

### Unknown
The job or candidate data does not contain enough information.

## Avoid false positives

Do not infer:
- Professional experience from a tutorial.
- Production experience from a lab.
- Certification completion from an in-progress course.
- Employment authorization from nationality/location alone.
- Years of experience from project duration unless explicitly supported.

## Output example

```json
{
  "job_id": "123",
  "required_matches": [
    {
      "requirement": "Python",
      "status": "strong",
      "evidence": ["skill:python", "project:evidentia"]
    }
  ],
  "gaps": [
    {
      "requirement": "2 years professional SOC experience",
      "status": "missing"
    }
  ],
  "uncertainties": [
    "Work authorization not stated"
  ]
}
```

## Scoring

If a numerical score is used, it must be explainable and must not hide hard gaps.

Prefer:
- Required coverage.
- Preferred coverage.
- Hard gaps.
- Evidence strength.

over a single opaque percentage.
