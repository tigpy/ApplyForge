"""Connector contracts. Job discovery and application filling are separate, swappable adapters."""
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class DiscoveredJob(BaseModel):
    external_id: str
    company: str
    title: str
    location: str = ""
    remote_type: str = "unknown"
    url: str = ""
    application_url: str = ""
    description: str = ""
    requirements: list[str] = []


from datetime import datetime


class FormField(BaseModel):
    ref: str  # opaque handle the connector uses to find the field again
    name: str
    label: str
    type: str = "text"  # text | email | tel | url | textarea | select | file | checkbox | radio
    required: bool = False
    options: list[str] = []
    placeholder: str = ""
    id: str = ""


class BrowserApplicationResult(BaseModel):
    status: str
    confirmation_text: str | None = None
    confirmation_url: str | None = None
    failure_reason: str | None = None
    blocked_reason: str | None = None
    manual_action_reason: str | None = None
    submitted_at: datetime | None = None
    page_type: str = "FORM_FOUND"
    fields_detected: list[dict] = []
    fields_filled: list[dict] = []
    resume_uploaded: str | None = None
    dry_run: bool = False


class JobConnector(ABC):
    name: str

    @abstractmethod
    def discover_jobs(self, query: str = "") -> list[DiscoveredJob]: ...

    @abstractmethod
    def get_job_details(self, external_id: str) -> DiscoveredJob: ...


class ApplicationConnector(ABC):
    """A 'page driver'. It performs primitive actions; ApplicationService decides what to fill."""

    name: str

    @abstractmethod
    def open(self, url: str) -> None: ...

    @abstractmethod
    def detect_blocker(self) -> str | None:
        """Return a reason if CAPTCHA / MFA / bot check is present, else None. Never try to bypass."""

    def detect_page_state(self) -> tuple[str, str | None]:
        """Detect current page classification (FORM_FOUND, CAPTCHA, CLOUDFLARE, LOGIN_REQUIRED, ALREADY_APPLIED, etc.)."""
        blocker = self.detect_blocker()
        if blocker:
            return "BLOCKED", blocker
        return "FORM_FOUND", None

    def get_current_url(self) -> str:
        """Return current URL after navigation."""
        return ""

    @abstractmethod
    def extract_fields(self) -> list[FormField]: ...

    @abstractmethod
    def fill_field(self, field: FormField, value: str) -> None: ...

    @abstractmethod
    def upload_resume(self, field: FormField, path: Path) -> None: ...

    @abstractmethod
    def submit(self) -> str | None:
        """Submit. Return confirmation text ONLY if the site confirmed it; otherwise None."""

    @abstractmethod
    def close(self) -> None: ...
