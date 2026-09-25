"""
Celery Background Tasks for ApplyForge
Supports: job discovery, matching, AI tailoring, resume generation, browser automation
"""
import asyncio
from typing import Any, Dict, List
from workers.celery_app import celery_app
from packages.domain.database import SessionLocal
from packages.domain.models import Application, Candidate, Job, JobRequirement, JobSource, Match
from packages.domain.enums import RequirementType
from packages.connectors.registry import connector_registry
from packages.matching.parser import parse_job_requirements
from packages.matching.engine import evaluate_match
from packages.documents.tailor import tailor_candidate_materials
from packages.documents.pdf_generator import generate_resume_pdf
from packages.llm.factory import get_llm_provider
from packages.shared.logger import logger

@celery_app.task(name="discover_jobs_task")
def discover_jobs_task(platform: str = "mock") -> Dict[str, Any]:
    db = SessionLocal()
    try:
        connector = connector_registry.get(platform)
        source = db.query(JobSource).filter(JobSource.name == platform).first()
        if not source:
            source = JobSource(name=platform, type=platform, configuration={})
            db.add(source)
            db.flush()

        raw_jobs = connector.search("python OR security")
        candidate = db.query(Candidate).first()

        imported = 0
        for raw in raw_jobs:
            norm = connector.normalize(raw)
            ext_id = norm.get("external_id")
            exists = db.query(Job).filter(Job.source_id == source.id, Job.external_id == ext_id).first()
            if not exists:
                job = Job(
                    source_id=source.id,
                    external_id=ext_id,
                    url=norm.get("url"),
                    title=norm.get("title"),
                    company=norm.get("company"),
                    location=norm.get("location"),
                    work_mode=norm.get("work_mode"),
                    employment_type=norm.get("employment_type"),
                    description_raw=norm.get("description_raw"),
                    description_normalized=norm.get("description_normalized")
                )
                db.add(job)
                db.flush()

                parsed = parse_job_requirements(job.description_raw)
                for r in parsed:
                    db.add(JobRequirement(
                        job_id=job.id,
                        requirement_type=r["requirement_type"],
                        text=r["text"],
                        normalized_skill=r["normalized_skill"],
                        mandatory=r["mandatory"],
                        evidence=r["evidence"]
                    ))
                db.flush()

                if candidate:
                    m = evaluate_match(candidate, job)
                    db.add(Match(
                        job_id=job.id,
                        candidate_id=candidate.id,
                        score=m["score"],
                        required_coverage=m["required_coverage"],
                        preferred_coverage=m["preferred_coverage"],
                        explanation=m["explanation"],
                        hard_gaps=m["hard_gaps"],
                        strengths=m["strengths"],
                        uncertainties=m["uncertainties"]
                    ))
                imported += 1
        db.commit()
        return {"platform": platform, "discovered": len(raw_jobs), "imported": imported}
    finally:
        db.close()

@celery_app.task(name="evaluate_match_task")
def evaluate_match_task(job_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        candidate = db.query(Candidate).first()
        if not job or not candidate:
            return {"error": "Job or Candidate not found"}
        res = evaluate_match(candidate, job)
        return res
    finally:
        db.close()

@celery_app.task(name="generate_resume_task")
def generate_resume_task(application_id: int) -> str:
    db = SessionLocal()
    try:
        app = db.query(Application).filter(Application.id == application_id).first()
        candidate = db.query(Candidate).first()
        if not app or not candidate:
            return ""
        llm = get_llm_provider()
        tailored = tailor_candidate_materials(candidate, app.job, app.resume, llm)
        pdf_path = generate_resume_pdf(candidate, app.job, app.resume, tailored)
        return str(pdf_path)
    finally:
        db.close()

@celery_app.task(name="browser_inspect_job_task")
def browser_inspect_job_task(url: str) -> Dict[str, Any]:
    from packages.automation.browser import PlaywrightBrowserService
    browser_svc = PlaywrightBrowserService(headless=True)
    return asyncio.run(browser_svc.extract_page_job_content(url))
