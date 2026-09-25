from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, JSON, String, Text, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

from packages.domain.enums import (
    ApplicationState, EmploymentType, RequirementType,
    SkillProficiency, WorkMode
)

Base = declarative_base()

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    work_authorization = Column(String(255), default="Citizen / Authorized")
    preferred_roles = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    work_preferences = Column(JSON, default=dict)
    summary = Column(Text, nullable=True)
    profile_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    educations = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="candidate", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="candidate", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate")

class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    degree = Column(String(255), nullable=False)
    field = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    status = Column(String(50), default="Completed")
    grade = Column(String(50), nullable=True)

    candidate = relationship("Candidate", back_populates="educations")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), default="General")
    proficiency = Column(SQLEnum(SkillProficiency), default=SkillProficiency.INTERMEDIATE)
    evidence = Column(JSON, default=list)

    candidate = relationship("Candidate", back_populates="skills")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    technologies = Column(JSON, default=list)
    url = Column(String(500), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    evidence = Column(JSON, default=list)

    candidate = relationship("Candidate", back_populates="projects")

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    organization = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(100), default="Full-time")
    description = Column(Text, nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    evidence = Column(JSON, default=list)

    candidate = relationship("Candidate", back_populates="experiences")

class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    status = Column(String(50), default="Active")
    date = Column(String(50), nullable=True)
    credential_url = Column(String(500), nullable=True)

    candidate = relationship("Candidate", back_populates="certifications")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    job_family = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    source = Column(String(100), default="manual")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    candidate = relationship("Candidate", back_populates="resumes")

class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)
    configuration = Column(JSON, default=dict)
    enabled = Column(Boolean, default=True)

    jobs = relationship("Job", back_populates="source")

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, index=True)
    url = Column(String(1000), nullable=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    work_mode = Column(SQLEnum(WorkMode), default=WorkMode.UNKNOWN)
    employment_type = Column(SQLEnum(EmploymentType), default=EmploymentType.FULL_TIME)
    description_raw = Column(Text, nullable=False)
    description_normalized = Column(Text, nullable=True)
    duplicate_fingerprint = Column(String(255), nullable=True, index=True)
    discovered_at = Column(DateTime(timezone=True), default=utc_now)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    closing_at = Column(DateTime(timezone=True), nullable=True)

    source = relationship("JobSource", back_populates="jobs")
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job")

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    requirement_type = Column(SQLEnum(RequirementType), default=RequirementType.SKILL)
    text = Column(Text, nullable=False)
    normalized_skill = Column(String(100), nullable=True, index=True)
    mandatory = Column(Boolean, default=True)
    evidence = Column(JSON, default=list)

    job = relationship("Job", back_populates="requirements")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    match_version = Column(Integer, default=1)
    score = Column(Float, default=0.0)
    required_coverage = Column(Float, default=0.0)
    preferred_coverage = Column(Float, default=0.0)
    explanation = Column(Text, nullable=False)
    hard_gaps = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    uncertainties = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("Job", back_populates="matches")
    candidate = relationship("Candidate")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    status = Column(SQLEnum(ApplicationState), default=ApplicationState.DISCOVERED, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    external_application_id = Column(String(255), nullable=True)
    application_url = Column(String(1000), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume")
    questions = relationship("ApplicationQuestion", back_populates="application", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="application", cascade="all, delete-orphan")

class ApplicationQuestion(Base):
    __tablename__ = "application_questions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    answer_source = Column(String(100), default="candidate_profile")
    requires_review = Column(Boolean, default=True)
    final_answer = Column(Text, nullable=True)

    application = relationship("Application", back_populates="questions")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    actor = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    payload_hash = Column(String(64), nullable=False)
    event_metadata = Column("metadata", JSON, default=dict)

    application = relationship("Application", back_populates="audit_events")
