"""Job discovery: pull from a connector, de-duplicate, extract requirements when missing."""
import re

from sqlalchemy.orm import Session

from app.ai.client import AIProvider
from app.connectors import get_job_connector
from app.errors import ServiceError
from app.models import Job


def make_fingerprint(company: str, title: str, location: str) -> str:
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()  # noqa: E731
    return "|".join(norm(x) for x in (company, title, location))


class JobService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db, self.ai = db, ai

    def discover(self, connector_name: str = "mock", query: str = "") -> tuple[int, list[Job]]:
        try:
            connector = get_job_connector(connector_name)
        except ValueError as exc:
            raise ServiceError(400, str(exc)) from exc
        new, jobs = 0, []
        for d in connector.discover_jobs(query):
            existing = self.db.query(Job).filter_by(source=connector.name, external_id=d.external_id).first()
            if existing:
                jobs.append(existing)
                continue
            requirements = d.requirements or self.ai.extract_requirements(d.description).requirements
            job = Job(
                company=d.company, title=d.title, location=d.location, remote_type=d.remote_type, url=d.url,
                application_url=d.application_url or d.url, description=d.description, requirements=requirements,
                source=connector.name, external_id=d.external_id,
                fingerprint=make_fingerprint(d.company, d.title, d.location),
            )
            self.db.add(job)
            jobs.append(job)
            new += 1
        self.db.commit()
        return new, jobs
