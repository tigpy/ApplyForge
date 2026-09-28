"""ORM -> API schema conversion (kept out of routers)."""
from sqlalchemy.orm import Session

from app.models import Application, ApplicationStatus, Job, MatchResult, Resume
from app.schemas import (
    ApplicationDetailOut,
    ApplicationOut,
    JobDetailOut,
    JobOut,
    MatchResultOut,
)


def latest_match(db: Session, job_id: int) -> MatchResult | None:
    return db.query(MatchResult).filter_by(job_id=job_id).order_by(MatchResult.id.desc()).first()


def match_out(db: Session, m: MatchResult) -> MatchResultOut:
    out = MatchResultOut.model_validate(m)
    resume = db.get(Resume, m.selected_resume_id) if m.selected_resume_id else None
    app = db.query(Application).filter_by(job_id=m.job_id).first()
    out.selected_resume_name = resume.filename if resume else None
    out.application_id = app.id if app else None
    out.application_status = ApplicationStatus(app.status) if app else None
    return out


def job_out(db: Session, job: Job) -> JobOut:
    out = JobOut.model_validate(job)
    m, app = latest_match(db, job.id), db.query(Application).filter_by(job_id=job.id).first()
    out.match_score = m.score if m else None
    out.selected_resume_id = m.selected_resume_id if m else None
    out.application_id = app.id if app else None
    return out


def job_detail_out(db: Session, job: Job) -> JobDetailOut:
    m = latest_match(db, job.id)
    return JobDetailOut(**job_out(db, job).model_dump(), description=job.description, match=match_out(db, m) if m else None)


def _app_fields(app: Application) -> dict:
    return {
        **{k: getattr(app, k) for k in ("id", "job_id", "resume_id", "status", "match_score", "application_url",
                                        "submitted_at", "failure_reason", "confirmation_text", "created_at", "updated_at")},
        "company": app.job.company, "role": app.job.title, "resume_name": app.resume.filename if app.resume else None,
    }


def application_out(app: Application) -> ApplicationOut:
    return ApplicationOut(**_app_fields(app))


def application_detail_out(app: Application) -> ApplicationDetailOut:
    return ApplicationDetailOut(**_app_fields(app), events=list(app.events))
