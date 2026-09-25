# Resume and Document Pipeline

## Goal

Maintain one master candidate profile and produce controlled variants.

## Pipeline

```text
Master Profile
      |
      +--> General Tech Resume
      +--> Cybersecurity Resume
      +--> SOC Resume
      +--> Backend Resume
      +--> Cloud/DevOps Resume
```

## Resume selection

Selection should consider:
- Job family.
- Required skills.
- Project relevance.
- Keywords.
- Experience requirements.

The system should recommend a resume variant, not silently change it after approval.

## Tailoring

Allowed changes:
- Summary emphasis.
- Skill ordering.
- Project ordering.
- Relevant bullet selection.
- Keyword alignment using truthful terms.

Every generated resume should retain:
- Candidate identity.
- Education.
- Dates.
- Verified experience.
- Verified projects.

## Document versioning

Every generated document must have:
- Source resume version.
- Job ID.
- Generation timestamp.
- Template version.
- AI/model version if applicable.

This makes applications reproducible.

## File naming

Example:

```text
Aryan-Singh_Resume_Cybersecurity_CompanyName_2026.pdf
```
