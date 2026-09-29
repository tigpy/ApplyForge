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

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str) and value.upper() == "SUBMITTED":
            return cls.APPLIED
        return None


class Recommendation(str, Enum):
    APPLY = "APPLY"
    SKIP = "SKIP"
