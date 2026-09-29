"""Automation service for running the full personal job-search and automatic application pipeline."""
import logging
from sqlalchemy.orm import Session

from app.ai.client import get_ai_provider
from app.config import settings
from app.connectors import get_application_connector
from app.models import Application, ApplicationStatus as S, CandidateProfile, Job
from app.schemas.api import AutomationRunResult
from app.services.application_service import apply_application
from app.services.job_service import JobService
from app.services.matching_service import run_match
from app.services.notification_service import get_notification_service
from app.services.resume_service import ResumeRepository

log = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = get_ai_provider()
        self.notifier = get_notification_service()

    def run_job_search(
        self, connector_name: str = "", query: str = "", auto_apply: bool = True,
        min_match_score: int | None = None,
    ) -> AutomationRunResult:
        resumes = ResumeRepository(self.db).list()
        if not resumes:
            raise ValueError("Upload at least one resume before running job search")

        profile = self.db.get(CandidateProfile, 1) or CandidateProfile()
        sources = [connector_name] if connector_name else (profile.preferred_job_sources or ["mock"])

        # 1. Discover jobs from connectors
        total_discovered = 0
        all_jobs: list[Job] = []
        job_service = JobService(self.db, self.ai)
        for src in sources:
            try:
                new_count, disc_jobs = job_service.discover(connector_name=src, query=query)
                total_discovered += new_count
                all_jobs.extend(disc_jobs)
            except Exception as exc:
                log.exception("Error discovering from source %s: %s", src, exc)

        # 2 & 3. Match jobs against all resumes
        matched_count = 0
        eligible_apps: list[Application] = []
        details: list[dict] = []

        unmatched_jobs = (
            self.db.query(Job)
            .filter(Job.status.in_([S.DISCOVERED.value, S.MATCHED.value]))
            .all()
        )
        jobs_to_process = list({j.id: j for j in (all_jobs + unmatched_jobs)}.values())

        for job in jobs_to_process:
            # Check exclusions
            if profile.excluded_companies and any(c.lower() in job.company.lower() for c in profile.excluded_companies):
                continue
            if profile.excluded_roles and any(r.lower() in job.title.lower() for r in profile.excluded_roles):
                continue

            try:
                run_match(self.db, job, self.ai)
                matched_count += 1
                app = self.db.query(Application).filter_by(job_id=job.id).first()
                if app and app.status == S.ELIGIBLE.value:
                    eligible_apps.append(app)
            except Exception as exc:
                log.exception("Error matching job %s: %s", job.id, exc)

        # 4. Filter opportunities by min_match_score if specified, and rank descending
        threshold = min_match_score if min_match_score is not None else 75
        qualifying_apps = [a for a in eligible_apps if (a.match_score or 0) >= threshold]
        qualifying_apps.sort(key=lambda a: (a.match_score or 0), reverse=True)

        # 5 & 6. Attempt applications automatically
        applied_count = 0
        blocked_count = 0
        manual_count = 0
        failed_count = 0

        max_apps = getattr(settings, "max_applications_per_run", 10)
        app_connector = get_application_connector()
        if auto_apply:
            for app in qualifying_apps:
                if applied_count >= max_apps:
                    log.info("Reached MAX_APPLICATIONS_PER_RUN cap (%d); stopping run", max_apps)
                    break
                try:
                    res = apply_application(
                        self.db,
                        app.id,
                        connector=app_connector,
                        ai=self.ai,
                        notifier=self.notifier,
                    )
                    status_name = res.status
                    if status_name in (S.APPLIED.value, "SUBMITTED"):
                        applied_count += 1
                    elif status_name in (S.REQUIRES_MANUAL_ACTION.value, "HUMAN_INTERVENTION_REQUIRED"):
                        manual_count += 1
                    elif status_name == S.BLOCKED.value:
                        blocked_count += 1
                    elif status_name == S.FAILED.value:
                        failed_count += 1

                    details.append({
                        "job_id": app.job_id,
                        "company": app.job.company,
                        "role": app.job.title,
                        "resume": app.resume.filename if app.resume else None,
                        "match_score": app.match_score,
                        "status": status_name,
                        "message": res.confirmation_text or res.failure_reason or "",
                    })
                except Exception as exc:
                    log.exception("Error applying to job %s: %s", app.job_id, exc)
                    failed_count += 1
                    details.append({
                        "job_id": app.job_id,
                        "company": app.job.company,
                        "role": app.job.title,
                        "resume": app.resume.filename if app.resume else None,
                        "match_score": app.match_score,
                        "status": "FAILED",
                        "message": str(exc),
                    })

        skipped_count = self.db.query(Application).filter(Application.status == S.SKIPPED.value).count()
        dup_count = self.db.query(Application).filter(Application.status == S.DUPLICATE.value).count()
        remaining_count = max(0, len(qualifying_apps) - (applied_count + blocked_count + manual_count + failed_count))

        return AutomationRunResult(
            discovered=total_discovered,
            matched=matched_count,
            eligible=len(qualifying_apps),
            applied=applied_count,
            requires_manual_action=manual_count,
            blocked=blocked_count,
            failed=failed_count,
            skipped=skipped_count,
            duplicate=dup_count,
            remaining=remaining_count,
            details=details,
        )


def run_job_application(db: Session, job_id: int, connector=None, dry_run: bool = False) -> Application:
    """End-to-end single job pipeline: match against all resumes -> select best -> apply safely -> return application."""
    from app.errors import ServiceError
    from app.services.application_service import _is_duplicate

    job = db.get(Job, job_id)
    if job is None:
        raise ServiceError(404, "Job not found")

    # Safety: Check if already applied
    existing_app = db.query(Application).filter_by(job_id=job.id).first()
    if existing_app is not None:
        if existing_app.status in (S.APPLIED.value, "SUBMITTED"):
            return existing_app
        if _is_duplicate(db, existing_app):
            existing_app.status = S.DUPLICATE.value
            existing_app.failure_reason = "ALREADY_APPLIED: Same job was already applied via another posting"
            db.commit()
            return existing_app

    # Check resumes exist
    resumes = ResumeRepository(db).list()
    if not resumes:
        raise ServiceError(409, "Upload at least one resume before applying")

    # Match against all resumes and select best
    match = run_match(db, job)
    app = db.query(Application).filter_by(job_id=job.id).first()
    if not app:
        raise ServiceError(500, "Application record could not be registered")

    # If score is below threshold, skip
    if match.recommendation == "SKIP" or app.status == S.SKIPPED.value:
        return app

    # If duplicate detected after matching
    if app.status == S.DUPLICATE.value:
        return app

    # Apply automatically (or simulate if dry_run)
    app = apply_application(db, app.id, connector=connector, dry_run=dry_run)
    return app


def run_automation(
    db: Session, connector_name: str = "", query: str = "", min_match_score: int | None = None
) -> AutomationRunResult:
    """Full automation workflow entrypoint."""
    service = AutomationService(db)
    return service.run_job_search(
        connector_name=connector_name,
        query=query,
        auto_apply=True,
        min_match_score=min_match_score,
    )
