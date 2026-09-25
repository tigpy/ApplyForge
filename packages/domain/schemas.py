from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from packages.domain.enums import (
    ApplicationState, EmploymentType, MatchStatus,
    RequirementType, SkillProficiency, WorkMode
)

class SkillBase(BaseModel):
    name: str
    category: str = "General"
    proficiency: SkillProficiency = SkillProficiency.INTERMEDIATE
    evidence: List[str] = Field(default_factory=list)

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    proficiency: Optional[SkillProficiency] = None
    evidence: Optional[List[str]] = None

class SkillOut(SkillBase):
    id: int
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

class EducationBase(BaseModel):
    degree: str
    field: str
    institution: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "Completed"
    grade: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationOut(EducationBase):
    id: int
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

class ExperienceBase(BaseModel):
    organization: str
    title: str
    type: str = "Full-time"
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceOut(ExperienceBase):
    id: int
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

class CertificationBase(BaseModel):
    name: str
    issuer: str
    status: str = "Active"
    date: Optional[str] = None
    credential_url: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationOut(CertificationBase):
    id: int
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

class ResumeBase(BaseModel):
    name: str
    job_family: str
    file_path: Optional[str] = None
    content_text: Optional[str] = None
    version: int = 1
    source: str = "manual"

class ResumeCreate(ResumeBase):
    pass

class ResumeOut(ResumeBase):
    id: int
    candidate_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    work_authorization: str = "Citizen / Authorized"
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    work_preferences: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    work_authorization: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    work_preferences: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None

class CandidateOut(CandidateBase):
    id: int
    profile_version: int
    created_at: datetime
    updated_at: datetime
    skills: List[SkillOut] = Field(default_factory=list)
    educations: List[EducationOut] = Field(default_factory=list)
    projects: List[ProjectOut] = Field(default_factory=list)
    experiences: List[ExperienceOut] = Field(default_factory=list)
    certifications: List[CertificationOut] = Field(default_factory=list)
    resumes: List[ResumeOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class JobSourceOut(BaseModel):
    id: int
    name: str
    type: str
    configuration: Dict[str, Any]
    enabled: bool
    model_config = ConfigDict(from_attributes=True)

class JobRequirementBase(BaseModel):
    requirement_type: RequirementType = RequirementType.SKILL
    text: str
    normalized_skill: Optional[str] = None
    mandatory: bool = True
    evidence: List[str] = Field(default_factory=list)

class JobRequirementOut(JobRequirementBase):
    id: int
    job_id: int
    model_config = ConfigDict(from_attributes=True)

class JobImportRequest(BaseModel):
    source_name: str = "manual"
    url: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = "Remote"
    work_mode: WorkMode = WorkMode.REMOTE
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    description_raw: str
    external_id: Optional[str] = None

class JobOut(BaseModel):
    id: int
    source_id: int
    external_id: str
    url: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    work_mode: WorkMode
    employment_type: EmploymentType
    description_raw: str
    description_normalized: Optional[str] = None
    discovered_at: datetime
    posted_at: Optional[datetime] = None
    requirements: List[JobRequirementOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class MatchItem(BaseModel):
    requirement: str
    status: MatchStatus
    evidence: List[str] = Field(default_factory=list)

class GapItem(BaseModel):
    requirement: str
    status: MatchStatus = MatchStatus.MISSING
    detail: Optional[str] = None

class MatchOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    score: float
    required_coverage: float
    preferred_coverage: float
    explanation: str
    hard_gaps: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    uncertainties: List[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApplicationQuestionOut(BaseModel):
    id: int
    application_id: int
    question: str
    answer: Optional[str] = None
    answer_source: str
    requires_review: bool
    final_answer: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ApplicationQuestionAnswerUpdate(BaseModel):
    final_answer: str

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    resume_id: Optional[int] = None
    notes: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    resume_id: Optional[int] = None
    status: ApplicationState
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    external_application_id: Optional[str] = None
    application_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobOut] = None
    questions: List[ApplicationQuestionOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class AuditEventOut(BaseModel):
    id: int
    application_id: Optional[int] = None
    event_type: str
    actor: str
    timestamp: datetime
    payload_hash: str
    event_metadata: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)
