# Job Application Automation Platform

## Purpose

Build a personal job-search and application-assistance platform that discovers relevant jobs, normalizes job descriptions, matches them against a structured candidate profile, prepares application materials, presents applications for human review, submits only through permitted mechanisms, and tracks outcomes.

The system is designed for a single candidate first. It must prioritize correctness, transparency, auditability, and platform compliance over maximum application volume.

## Core principle

```text
Discover -> Parse -> Match -> Prepare -> Human Review -> Submit -> Track
```

The system must never silently submit an application that has not been approved by the user.

## Initial target

The first version should support:
- Multiple job sources/connectors.
- A master candidate profile.
- Multiple resume variants.
- Job parsing and normalization.
- Deterministic + AI-assisted matching.
- Application-question assistance.
- Human approval before submission.
- Application tracking.
- Duplicate detection.
- Full audit logs.

## Non-goals

Do not build:
- CAPTCHA bypass.
- Anti-bot or rate-limit evasion.
- Credential theft or session hijacking.
- Automatic submission that violates a platform's rules.
- Fabricated qualifications, experience, certifications, answers, or work history.
- High-volume spam application behavior.

## Success criteria

A user should be able to:
1. Configure their candidate profile once.
2. Connect permitted job sources.
3. Import jobs.
4. See why each job matches or does not match.
5. Select a resume/profile variant.
6. Generate tailored materials.
7. Review every important application field.
8. Approve or reject submission.
9. Track the application afterward.
10. Audit exactly what was submitted.
