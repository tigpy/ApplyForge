"""Pydantic request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ApplicationStatus, Recommendation


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthOut(BaseModel):
    status: str
    version: str
    ai_provider: str
    application_connector: str
    notification_mode: str


# ---- resumes
class ResumeOut(ORM):
    id: int
    filename: str
    display_name: str
    tags: list[str]
    target_role: str | None
    extracted_chars: int
    extracted_text: str = ""
    created_at: datetime


# ---- matching (the contract between matcher, DB and API)
class ResumeScore(BaseModel):
    resume_id: int
    resume_name: str = ""
    score: int


class MatchResultData(BaseModel):
    job_id: int
    selected_resume_id: int | None
    score: int
    strengths: list[str]
    missing_requirements: list[str]
    reasons: list[str]
    recommendation: Recommendation
    resume_scores: list[ResumeScore] = []


class MatchResultOut(MatchResultData, ORM):
    id: int
    created_at: datetime
    selected_resume_name: str | None = None
    application_id: int | None = None
    application_status: ApplicationStatus | None = None


# ---- jobs
class JobOut(ORM):
    id: int
    company: str
    title: str
    location: str
    remote_type: str
    url: str
    application_url: str
    source: str
    requirements: list[str]
    discovered_at: datetime
    status: ApplicationStatus
    match_score: int | None = None
    selected_resume_id: int | None = None
    application_id: int | None = None


class JobDetailOut(JobOut):
    description: str
    match: MatchResultOut | None = None


class DiscoverRequest(BaseModel):
    query: str = ""
    connector: str = "mock"


class DiscoverResponse(BaseModel):
    discovered: int  # newly stored jobs (existing ones are not duplicated)
    jobs: list[JobOut]


# ---- applications
class ApplicationEventOut(ORM):
    id: int
    event: str
    details: str
    created_at: datetime


class ApplicationOut(ORM):
    id: int
    job_id: int
    resume_id: int | None
    status: ApplicationStatus
    match_score: int | None
    application_url: str
    submitted_at: datetime | None
    failure_reason: str | None
    confirmation_text: str | None
    created_at: datetime
    updated_at: datetime
    company: str
    role: str
    resume_name: str | None


class ApplicationDetailOut(ApplicationOut):
    events: list[ApplicationEventOut]


# ---- profile / settings
class ProfileBase(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    education: list[str] = []
    skills: list[str] = []
    experience: list[str] = []
    facts: dict[str, str] = {}
    target_roles: list[str] = []
    preferred_locations: list[str] = []
    remote_preference: str = "all"
    min_experience: int = 0
    salary_preference: str = ""
    excluded_roles: list[str] = []
    excluded_companies: list[str] = []
    preferred_job_sources: list[str] = ["mock"]


class ProfileIn(ProfileBase):
    pass


class ProfileOut(ProfileBase, ORM):
    pass


class TestEmailOut(BaseModel):
    sent: bool
    mode: str
    detail: str


# ---- automation run
class AutomationRunRequest(BaseModel):
    connector: str = ""  # empty = use preferred_job_sources from profile
    query: str = ""
    auto_apply: bool = True  # whether to automatically apply to eligible matches


class AutomationRunResult(BaseModel):
    discovered: int
    matched: int
    eligible: int
    applied: int
    requires_manual_action: int
    blocked: int
    failed: int
    skipped: int
    duplicate: int
    details: list[dict] = []
