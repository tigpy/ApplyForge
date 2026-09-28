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


class FormField(BaseModel):
    ref: str  # opaque handle the connector uses to find the field again
    name: str
    label: str
    type: str = "text"  # text | email | tel | url | textarea | select | file | checkbox | radio
    required: bool = False
    options: list[str] = []


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
