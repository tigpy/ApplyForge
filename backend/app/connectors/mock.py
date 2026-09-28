"""Offline connectors so the whole workflow runs without any real website."""
from pathlib import Path

from app.connectors.base import ApplicationConnector, DiscoveredJob, FormField, JobConnector

_MOCK_JOBS = [
    DiscoveredJob(
        external_id="example-corp-jsa", company="Example Corp", title="Junior Security Analyst",
        location="Toronto, Canada", remote_type="hybrid", url="mock://jobs/example-corp-jsa",
        application_url="mock://apply/example-corp-jsa",
        description="Monitor security alerts and respond to incidents in our SOC.",
        requirements=["Python scripting", "Linux administration", "SIEM tools", "Incident response", "Networking fundamentals"],
    ),
    DiscoveredJob(
        external_id="acme-backend", company="Acme Software", title="Backend Python Developer",
        location="Dublin, Ireland", remote_type="remote", url="mock://jobs/acme-backend",
        application_url="mock://apply/acme-backend",
        description="Build APIs for our platform.\nRequirements:\n- Python and FastAPI\n- SQL databases\n- REST API design\n- Git",
    ),  # requirements intentionally empty -> exercises AI requirement extraction
    DiscoveredJob(
        external_id="shield-labs-captcha", company="Shield Labs", title="Security Engineer",
        location="Sydney, Australia", remote_type="onsite", url="mock://jobs/shield-labs",
        application_url="mock://apply/shield-labs-captcha",
        description="Own detection engineering.",
        requirements=["Python", "SIEM", "Linux", "Incident response"],
    ),  # apply page shows a CAPTCHA -> BLOCKED
    DiscoveredJob(
        external_id="northwind-question", company="Northwind", title="SOC Analyst",
        location="Vancouver, Canada", remote_type="hybrid", url="mock://jobs/northwind",
        application_url="mock://apply/northwind-question",
        description="Tier 1/2 SOC analyst.",
        requirements=["SIEM", "Networking", "Log analysis", "Linux"],
    ),  # apply page has a mandatory question needing a stored fact -> BLOCKED unless answered
]


class MockJobConnector(JobConnector):
    name = "mock"

    def discover_jobs(self, query: str = "") -> list[DiscoveredJob]:
        q = query.lower().strip()
        return [j.model_copy() for j in _MOCK_JOBS if not q or q in f"{j.title} {j.company}".lower()]

    def get_job_details(self, external_id: str) -> DiscoveredJob:
        for job in _MOCK_JOBS:
            if job.external_id == external_id:
                return job.model_copy()
        raise KeyError(external_id)


class MockApplicationConnector(ApplicationConnector):
    """Simulates an application form. Behaviour is driven by the mock:// URL."""

    name = "mock"

    def __init__(self) -> None:
        self.url = ""
        self.values: dict[str, str] = {}
        self.uploaded: Path | None = None
        self.closed = False

    def open(self, url: str) -> None:
        if not url.startswith("mock://apply/"):
            raise ValueError("MockApplicationConnector only opens mock://apply/... URLs")
        self.url = url

    def detect_blocker(self) -> str | None:
        return "CAPTCHA detected on application page" if "captcha" in self.url else None

    def extract_fields(self) -> list[FormField]:
        fields = [
            FormField(ref="full_name", name="full_name", label="Full name", type="text", required=True),
            FormField(ref="email", name="email", label="Email address", type="email", required=True),
            FormField(ref="phone", name="phone", label="Phone number", type="tel", required=False),
            FormField(ref="linkedin", name="linkedin", label="LinkedIn URL", type="url", required=False),
            FormField(ref="resume", name="resume", label="Resume (PDF)", type="file", required=True),
        ]
        if "question" in self.url:
            fields.append(FormField(ref="auth", name="auth", label="Are you legally authorized to work in Canada?",
                                    type="select", required=True, options=["Yes", "No"]))
        return fields

    def fill_field(self, field: FormField, value: str) -> None:
        self.values[field.ref] = value

    def upload_resume(self, field: FormField, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError("Resume file not found")
        self.uploaded = path

    def submit(self) -> str | None:
        required = [f.ref for f in self.extract_fields() if f.required and f.type != "file"]
        if self.uploaded is None or any(not self.values.get(r) for r in required):
            return None  # the mock site rejects incomplete forms -> no confirmation
        return "Mock: application received. Thank you for applying!"

    def close(self) -> None:
        self.closed = True
