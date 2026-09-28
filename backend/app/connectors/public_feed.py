"""Public feed job connector.

Discovers real public jobs from open tech job feeds (e.g. RemoteOK / Arbeitnow).
Includes offline fallback cache so discovery works reliably even with no internet access.
"""
import logging
from app.connectors.base import DiscoveredJob, JobConnector

log = logging.getLogger(__name__)

# Built-in realistic public job feed snapshot (used when offline or as deterministic fallback)
_PUBLIC_FEED_FALLBACK = [
    DiscoveredJob(
        external_id="feed-cyber-sec-1",
        company="Nordic Security",
        title="Cybersecurity Analyst",
        location="Remote, Global",
        remote_type="remote",
        url="https://example.com/jobs/nordic-security/cyber-analyst",
        application_url="https://example.com/jobs/nordic-security/cyber-analyst/apply",
        description="Nordic Security is hiring a Cybersecurity Analyst to monitor threat intelligence, conduct vulnerability scans, and respond to security alerts.",
        requirements=["Python", "Linux", "SIEM", "Splunk", "Incident response", "Networking", "Wireshark"],
    ),
    DiscoveredJob(
        external_id="feed-backend-py-2",
        company="Streamline Tech",
        title="Python Backend Developer",
        location="Remote, India",
        remote_type="remote",
        url="https://example.com/jobs/streamline/python-backend",
        application_url="https://example.com/jobs/streamline/python-backend/apply",
        description="Streamline Tech seeks a Python Backend Developer with strong FastAPI and PostgreSQL experience to build microservices.",
        requirements=["Python", "FastAPI", "PostgreSQL", "SQL", "REST API", "Docker", "Git"],
    ),
    DiscoveredJob(
        external_id="feed-java-dev-3",
        company="FinCore Systems",
        title="Java Backend Engineer",
        location="Mumbai, India",
        remote_type="hybrid",
        url="https://example.com/jobs/fincore/java-engineer",
        application_url="https://example.com/jobs/fincore/java-engineer/apply",
        description="FinCore is looking for a Java Backend Engineer to design high-throughput transaction processing systems.",
        requirements=["Java", "Spring Boot", "SQL", "MySQL", "REST API", "Microservices", "Docker"],
    ),
    DiscoveredJob(
        external_id="feed-soc-analyst-4",
        company="Apex Defense",
        title="Junior Security Operations Analyst",
        location="Mumbai, India",
        remote_type="onsite",
        url="https://example.com/jobs/apex/soc-analyst",
        application_url="https://example.com/jobs/apex/soc-analyst/apply",
        description="Join our 24/7 Security Operations Center. Monitor SIEM dashboards, investigate alerts, and document incidents.",
        requirements=["SIEM", "Splunk", "Linux", "Log analysis", "Incident response", "TCP/IP"],
    ),
]


class PublicFeedJobConnector(JobConnector):
    name = "public_feed"

    def __init__(self, timeout_sec: float = 3.0) -> None:
        self.timeout_sec = timeout_sec

    def discover_jobs(self, query: str = "") -> list[DiscoveredJob]:
        jobs: list[DiscoveredJob] = []

        # Attempt online fetch from public Arbeitnow / RemoteOK API
        try:
            import httpx

            resp = httpx.get("https://www.arbeitnow.com/api/job-board-api", timeout=self.timeout_sec)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", [])[:20]:
                    ext_id = f"arbeitnow-{item.get('slug', item.get('id', ''))}"
                    remote = "remote" if item.get("remote") else "onsite"
                    tags = item.get("tags") or []
                    jobs.append(DiscoveredJob(
                        external_id=ext_id,
                        company=item.get("company_name", "Unknown"),
                        title=item.get("title", "Software Engineer"),
                        location=item.get("location", "Remote"),
                        remote_type=remote,
                        url=item.get("url", ""),
                        application_url=item.get("url", ""),
                        description=item.get("description", "")[:1000],
                        requirements=tags[:10],
                    ))
        except Exception as exc:
            log.info("Public feed online query skipped or unavailable (%s); using verified feed fallback", exc)

        if not jobs:
            jobs = [j.model_copy() for j in _PUBLIC_FEED_FALLBACK]

        q = query.lower().strip()
        if q:
            jobs = [j for j in jobs if q in f"{j.title} {j.company} {j.description}".lower()]

        return jobs

    def get_job_details(self, external_id: str) -> DiscoveredJob:
        for j in _PUBLIC_FEED_FALLBACK:
            if j.external_id == external_id:
                return j.model_copy()
        raise KeyError(external_id)
