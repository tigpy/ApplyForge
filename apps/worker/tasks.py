"""
Background Asynchronous Tasks for Discovery & Ingestion
"""
from apps.worker.celery_app import celery_app
from packages.domain.database import SessionLocal
from packages.domain.models import JobPosting, CandidateProfile, Application
from packages.connectors.registry import get_connector_registry
from packages.matching.parser import DeterministicJobParser
from packages.matching.engine import MatchingEngine
from packages.documents.tailor import DocumentTailor

@celery_app.task(name="discover_jobs_task")
def discover_jobs_task(platform: str = "mock"):
    db = SessionLocal()
    try:
        registry = get_connector_registry()
        connector = registry.get(platform)
        if not connector:
            return {"error": f"Unknown platform: {platform}"}
            
        raw_jobs = connector.discover_jobs()
        parser = DeterministicJobParser()
        profile = db.query(CandidateProfile).first()
        engine = MatchingEngine(profile=profile) if profile else None
        
        imported = 0
        for raw in raw_jobs:
            normalized = connector.normalize_job(raw)
            exists = db.query(JobPosting).filter(
                (JobPosting.title == normalized.get("title")) &
                (JobPosting.company == normalized.get("company"))
            ).first()
            if not exists:
                parsed_reqs = parser.parse(normalized.get("description", ""))
                job = JobPosting(
                    external_id=normalized.get("external_id"),
                    title=normalized.get("title"),
                    company=normalized.get("company"),
                    location=normalized.get("location"),
                    url=normalized.get("url"),
                    source=platform,
                    description=normalized.get("description"),
                    parsed_requirements=parsed_reqs
                )
                if engine:
                    m = engine.match(job)
                    job.match_score = m["overall_score"]
                db.add(job)
                imported += 1
        db.commit()
        return {"discovered": len(raw_jobs), "imported": imported}
    finally:
        db.close()
