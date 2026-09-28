"""Automation service for running the full personal job-search and automatic application pipeline."""
import logging
from sqlalchemy.orm import Session

from app.ai.client import get_ai_provider
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
        self, connector_name: str = "", query: str = "", auto_apply: bool = True
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

        # 4. Rank opportunities by match score descending
        eligible_apps.sort(key=lambda a: (a.match_score or 0), reverse=True)

        # 5 & 6. Attempt applications automatically
        applied_count = 0
        blocked_count = 0
        manual_count = 0
        failed_count = 0

        app_connector = get_application_connector()
        if auto_apply:
            for app in eligible_apps:
                try:
                    res = apply_application(
                        self.db,
                        app.id,
                        connector=app_connector,
                        ai=self.ai,
                        notifier=self.notifier,
                    )
                    status_name = res.status
                    if status_name == S.APPLIED.value:
                        applied_count += 1
                    elif status_name == S.REQUIRES_MANUAL_ACTION.value:
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

        return AutomationRunResult(
            discovered=total_discovered,
            matched=matched_count,
            eligible=len(eligible_apps),
            applied=applied_count,
            requires_manual_action=manual_count,
            blocked=blocked_count,
            failed=failed_count,
            skipped=skipped_count,
            duplicate=dup_count,
            details=details,
        )
