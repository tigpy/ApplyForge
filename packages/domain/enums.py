from enum import Enum

class ApplicationState(str, Enum):
    DISCOVERED = "DISCOVERED"
    SAVED = "SAVED"
    ANALYZED = "ANALYZED"
    PREPARING = "PREPARING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    APPROVED = "APPROVED"
    SKIP = "SKIP"
    SUBMITTING = "SUBMITTING"
    SUBMITTED = "SUBMITTED"
    FAILED = "FAILED"
    FOLLOW_UP = "FOLLOW_UP"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"
    CLOSED = "CLOSED"

class WorkMode(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"

class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    UNKNOWN = "UNKNOWN"

class SkillProficiency(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"

class MatchStatus(str, Enum):
    STRONG = "strong"
    TRANSFERABLE = "transferable"
    MISSING = "missing"
    UNKNOWN = "unknown"

class RequirementType(str, Enum):
    SKILL = "skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    WORK_AUTH = "work_auth"
    OTHER = "other"
