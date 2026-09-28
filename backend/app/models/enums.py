from enum import Enum


class ApplicationStatus(str, Enum):
    """Shared by Job.status (mirrors its application) and Application.status."""

    DISCOVERED = "DISCOVERED"
    MATCHED = "MATCHED"
    ELIGIBLE = "ELIGIBLE"
    QUEUED = "QUEUED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    DUPLICATE = "DUPLICATE"
    BLOCKED = "BLOCKED"
    REQUIRES_MANUAL_ACTION = "REQUIRES_MANUAL_ACTION"


class Recommendation(str, Enum):
    APPLY = "APPLY"
    SKIP = "SKIP"
