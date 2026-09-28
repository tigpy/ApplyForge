from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.client import get_ai_provider
from app.database import get_db
from app.errors import ServiceError
from app.models import Job
from app.presenters import job_detail_out, job_out, match_out
from app.schemas import (
    AutomationRunRequest,
    AutomationRunResult,
    DiscoverRequest,
    DiscoverResponse,
    JobDetailOut,
    JobOut,
    MatchResultOut,
)
from app.services.job_service import JobService
from app.services.matching_service import run_match

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise ServiceError(404, "Job not found")
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return [job_out(db, j) for j in db.query(Job).order_by(Job.id).all()]


@router.post("/discover", response_model=DiscoverResponse)
def discover_jobs(body: DiscoverRequest | None = None, db: Session = Depends(get_db)):
    body = body or DiscoverRequest()
    new, jobs = JobService(db, get_ai_provider()).discover(body.connector, body.query)
    return DiscoverResponse(discovered=new, jobs=[job_out(db, j) for j in jobs])


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_detail_out(db, _get_job(db, job_id))


@router.post("/{job_id}/match", response_model=MatchResultOut)
def match_job(job_id: int, db: Session = Depends(get_db)):
    return match_out(db, run_match(db, _get_job(db, job_id)))


@router.post("/run-search", response_model=AutomationRunResult)
def run_job_search(body: AutomationRunRequest | None = None, db: Session = Depends(get_db)):
    from app.services.automation_service import AutomationService

    body = body or AutomationRunRequest()
    try:
        service = AutomationService(db)
        return service.run_job_search(
            connector_name=body.connector, query=body.query, auto_apply=body.auto_apply
        )
    except ValueError as exc:
        raise ServiceError(400, str(exc)) from exc
