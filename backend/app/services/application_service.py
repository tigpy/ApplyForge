"""Application state machine + the apply flow. Browser specifics live behind ApplicationConnector."""
import logging
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.ai.application_answers import accept_answer
from app.ai.client import AIProvider, get_ai_provider
from app.connectors import get_application_connector
from app.connectors.base import ApplicationConnector, FormField
from app.errors import ServiceError
from app.models import Application, ApplicationEvent, ApplicationStatus as S, CandidateProfile, Job, MatchResult, utcnow
from app.models.enums import Recommendation
from app.security import validate_external_url
from app.services.notification_service import NotificationService, build_application_notification, get_notification_service

log = logging.getLogger(__name__)

ALLOWED: dict[S, set[S]] = {
    S.DISCOVERED: {S.MATCHED, S.SKIPPED},
    S.MATCHED: {S.ELIGIBLE, S.SKIPPED, S.DUPLICATE},
    S.ELIGIBLE: {S.QUEUED, S.SKIPPED, S.DUPLICATE, S.MATCHED},  # MATCHED = re-match
    S.QUEUED: {S.APPLYING, S.SKIPPED},
    S.APPLYING: {S.APPLIED, S.FAILED, S.BLOCKED, S.REQUIRES_MANUAL_ACTION, S.DUPLICATE},
    S.FAILED: {S.QUEUED, S.DUPLICATE},  # retry
    S.BLOCKED: {S.QUEUED, S.DUPLICATE},  # retry after the user fixes the cause
    S.REQUIRES_MANUAL_ACTION: {S.QUEUED, S.DUPLICATE},  # retry after answering required facts
    S.SKIPPED: {S.MATCHED},  # re-match after uploading a better resume
    S.APPLIED: set(),
    S.DUPLICATE: set(),
}


def can_transition(current: S, new: S) -> bool:
    return new in ALLOWED[current]


def log_event(db: Session, app: Application, event: str, details: str = "") -> None:
    db.add(ApplicationEvent(application_id=app.id, event=event, details=details))


def transition(db: Session, app: Application, new: S, details: str = "") -> None:
    current = S(app.status)
    if not can_transition(current, new):
        raise ServiceError(409, f"Invalid status transition {current.value} -> {new.value}")
    app.status = new.value
    app.updated_at = utcnow()
    app.job.status = new.value
    log_event(db, app, new.value, details)
    db.flush()


def _is_duplicate(db: Session, app: Application) -> bool:
    """Same fingerprint (company/title/location) already APPLIED via another job row."""
    return (
        db.query(Application).join(Job, Application.job_id == Job.id)
        .filter(Job.fingerprint == app.job.fingerprint, Application.status == S.APPLIED.value, Application.id != app.id)
        .first() is not None
    )


def register_match(db: Session, job: Job, match: MatchResult) -> Application:
    """Create/refresh the Application for a job after matching and decide ELIGIBLE / SKIPPED / DUPLICATE."""
    app = db.query(Application).filter_by(job_id=job.id).first()
    if app is None:
        app = Application(job_id=job.id, status=S.MATCHED.value)
        db.add(app)
        db.flush()
        app.job = job
    elif S(app.status) in (S.ELIGIBLE, S.SKIPPED):
        transition(db, app, S.MATCHED, "re-matched")
    elif S(app.status) != S.MATCHED:
        return app  # queued/applying/applied/failed/blocked: never overwritten by a re-match
    app.resume_id, app.match_score, app.application_url = match.selected_resume_id, match.score, job.application_url
    job.status = S.MATCHED.value
    log_event(db, app, "MATCHED", f"score {match.score}, recommendation {match.recommendation}")
    if match.recommendation == Recommendation.SKIP.value:
        transition(db, app, S.SKIPPED, f"score {match.score} below threshold")
    elif _is_duplicate(db, app):
        transition(db, app, S.DUPLICATE, "same job already applied")
    else:
        transition(db, app, S.ELIGIBLE)
    db.flush()
    return app


# ---------------------------------------------------------------- form planning
_UNSUPPORTED_TYPES = set()  # Checkbox and radio are now supported


def build_facts(profile: CandidateProfile) -> dict[str, str]:
    facts = {k: getattr(profile, k) for k in ("name", "email", "phone", "location", "linkedin", "github", "portfolio")}
    for k in ("skills", "education", "experience"):
        facts[k] = "; ".join(getattr(profile, k) or [])
    facts.update(profile.facts or {})
    return {k: v for k, v in facts.items() if v}


def _match_option(options: list[str], target: str) -> str:
    """Finds best matching option from dropdown or radio options."""
    if not options or not target:
        return target
    target_low = target.lower().strip()
    # 1. Exact match
    for opt in options:
        if opt.strip().lower() == target_low:
            return opt
    # 2. Binary Yes/No matching
    if target_low in ("yes", "true", "1", "authorized"):
        for opt in options:
            if opt.strip().lower().startswith("yes") or "authorized" in opt.lower():
                return opt
    elif target_low in ("no", "false", "0"):
        for opt in options:
            if opt.strip().lower().startswith("no") or "will not" in opt.lower():
                return opt
    # 3. Substring matching
    for opt in options:
        if target_low in opt.lower() or opt.lower() in target_low:
            return opt
    return options[0] if options else target


def _known_value(field_name: str, field_type: str, profile: CandidateProfile) -> str:
    low = (field_name or "").lower().strip()
    facts = profile.facts or {}

    # 1. Names
    parts = (profile.name or "").split()
    if any(k in low for k in ("first name", "firstname", "fname", "first_name", "given name", "forename")):
        return parts[0] if parts else ""
    if any(k in low for k in ("last name", "lastname", "lname", "last_name", "family name", "surname")):
        return parts[-1] if len(parts) > 1 else ""
    if any(k in low for k in ("full name", "your name", "candidate name", "legal name")) or low == "name" or low.endswith(" name"):
        return profile.name or ""

    # 2. Contact & Socials
    if any(k in low for k in ("email", "e-mail", "mail")) or field_type == "email":
        return profile.email or ""
    if any(k in low for k in ("phone", "telephone", "mobile", "cell", "contact number")) or field_type == "tel":
        return profile.phone or ""
    if "linkedin" in low:
        return profile.linkedin or ""
    if "github" in low:
        return profile.github or ""
    if any(k in low for k in ("portfolio", "website", "personal site", "personal url", "homepage", "web site")):
        return profile.portfolio or facts.get("portfolio", "")

    # 3. Work authorization
    if any(k in low for k in ("authorized to work", "work authorization", "legally authorized", "eligible to work", "right to work", "work permit", "authorized in", "authorized")):
        for key in ("work_authorization", "authorized_to_work", "work_auth", "authorized"):
            if key in facts:
                return str(facts[key])
        return ""

    # 4. Sponsorship
    if any(k in low for k in ("sponsorship", "visa sponsorship", "require visa", "require sponsorship", "future require")):
        for key in ("sponsorship", "visa_sponsorship", "require_sponsorship"):
            if key in facts:
                return str(facts[key])
        return "No" if facts.get("work_authorization") else ""

    # 5. Location / City
    if any(k in low for k in ("city", "town")):
        if facts.get("city"):
            return facts["city"]
        return profile.location.split(",")[0].strip() if profile.location else ""
    if any(k in low for k in ("location", "address", "residence", "country", "state", "postal", "zip")):
        return facts.get("location") or profile.location or ""

    # 6. Years of experience
    if any(k in low for k in ("years of experience", "total experience", "how many years", "experience (years)", "years of professional")):
        for key in ("years_of_experience", "experience_years", "experience"):
            if key in facts:
                return str(facts[key])
        return str(profile.min_experience) if profile.min_experience > 0 else ""

    # 7. Education / Degree
    if any(k in low for k in ("highest degree", "degree level", "degree", "highest level of education", "qualification")):
        for key in ("education", "degree", "highest_degree"):
            if key in facts:
                return str(facts[key])
        return profile.education[0] if profile.education else ""

    # 8. Cover letter / Note to hiring manager
    if any(k in low for k in ("cover letter", "message to hiring manager", "additional notes", "coverletter", "note to recruiter", "summary")):
        for key in ("cover_letter", "summary", "notes"):
            if key in facts:
                return str(facts[key])
        return "Please find attached my resume for consideration. Thank you."

    # 9. Consent / Terms / Agreement checkbox
    if field_type == "checkbox" and any(k in low for k in ("agree", "terms", "privacy", "consent", "certify", "acknowledge")):
        return "Yes"

    # 10. Check facts directly for any matching key
    for k, v in facts.items():
        if k.lower() in low or low in k.lower():
            return str(v)

    return ""


@dataclass
class FillPlan:
    values: list[tuple[FormField, str]] = field(default_factory=list)
    file_field: FormField | None = None
    unknown: list[str] = field(default_factory=list)  # mandatory fields we cannot answer truthfully


def plan_fill(fields: list[FormField], profile: CandidateProfile, ai: AIProvider) -> FillPlan:
    plan, facts = FillPlan(), build_facts(profile)
    for f in fields:
        name = f.label or f.name
        if f.type == "file":
            plan.file_field = plan.file_field or f
            continue

        value = _known_value(name, f.type, profile)
        if not value and f.required:
            value = accept_answer(ai.answer_question(name, facts), f.options) or ""

        if value and f.options:
            value = _match_option(f.options, value)

        if value:
            plan.values.append((f, value))
        elif f.required:
            plan.unknown.append(name)
    return plan


# ---------------------------------------------------------------- apply flow
@dataclass
class Outcome:
    status: S
    reason: str | None = None
    confirmation: str | None = None
    details: dict | None = None


def _execute(
    db: Session,
    app: Application,
    conn: ApplicationConnector,
    profile: CandidateProfile,
    ai: AIProvider,
    dry_run: bool = False,
) -> Outcome:
    resume = app.resume
    if resume is None or not Path(resume.path).exists():
        return Outcome(S.FAILED, "Selected resume file is missing")

    if conn.name != "mock":
        validate_external_url(app.application_url)

    conn.open(app.application_url)
    log_event(db, app, "OPENED", app.application_url)

    # Detect blockers / page state
    page_type, reason = conn.detect_page_state()
    if page_type == "ALREADY_APPLIED" or (reason and "already applied" in reason.lower()):
        return Outcome(S.DUPLICATE, reason or "Already applied on site")
    if reason:
        return Outcome(S.BLOCKED, reason)

    fields = conn.extract_fields()
    log_event(db, app, "FIELDS_EXTRACTED", f"{len(fields)} fields")

    plan = plan_fill(fields, profile, ai)
    if plan.unknown:
        return Outcome(
            S.REQUIRES_MANUAL_ACTION,
            "Manual input needed for mandatory field(s): " + ", ".join(plan.unknown),
        )

    log_event(db, app, "RESUME_SELECTED", resume.filename)
    if plan.file_field:
        conn.upload_resume(plan.file_field, Path(resume.path))

    for f, value in plan.values:
        conn.fill_field(f, value)

    log_event(db, app, "FORM_FILLED", ", ".join(f.label or f.name for f, _ in plan.values))  # labels only, no PII

    if dry_run:
        fields_summary = [f.label or f.name for f, _ in plan.values]
        log_event(db, app, "DRY_RUN_COMPLETED", f"Simulated {len(fields_summary)} fields, resume: {resume.filename}")
        return Outcome(
            status=S.ELIGIBLE,
            confirmation=f"DRY RUN PASSED: {len(plan.values)} fields filled, resume '{resume.filename}' ready to upload. Submission was simulated (not submitted).",
            details={
                "dry_run": True,
                "fields_detected": [f.model_dump() for f in fields],
                "fields_planned": [{"name": f.label or f.name, "value": v} for f, v in plan.values],
                "resume_selected": resume.filename,
            },
        )

    if reason := conn.detect_blocker():
        return Outcome(S.BLOCKED, reason)

    confirmation = conn.submit()
    log_event(db, app, "SUBMITTED")
    if confirmation:
        return Outcome(S.APPLIED, confirmation=confirmation)
    return Outcome(S.FAILED, "Submission was not confirmed by the site (not marked as applied)")


def apply_application(
    db: Session, application_id: int, connector: ApplicationConnector | None = None,
    ai: AIProvider | None = None, notifier: NotificationService | None = None,
    dry_run: bool = False,
) -> Application:
    app = db.get(Application, application_id)
    if app is None:
        raise ServiceError(404, "Application not found")
    if S(app.status) not in (S.ELIGIBLE, S.FAILED, S.BLOCKED, S.REQUIRES_MANUAL_ACTION):
        raise ServiceError(409, f"Cannot apply from status {app.status}")
    if _is_duplicate(db, app):
        transition(db, app, S.DUPLICATE, "same job already applied")
        db.commit()
        return app

    conn = connector or get_application_connector()
    profile = db.get(CandidateProfile, 1) or CandidateProfile()

    if dry_run:
        try:
            outcome = _execute(db, app, conn, profile, ai or get_ai_provider(), dry_run=True)
        except Exception as exc:  # noqa: BLE001
            log.exception("Dry run error for application %s", application_id)
            outcome = Outcome(S.FAILED, f"Dry-run error: {exc}")
        finally:
            conn.close()

        if outcome.status == S.ELIGIBLE:
            app.confirmation_text = outcome.confirmation
            app.failure_reason = None
        else:
            app.failure_reason = outcome.reason
            transition(db, app, outcome.status, outcome.reason or "")
        db.commit()
        return app

    transition(db, app, S.QUEUED)
    db.commit()
    claimed = db.execute(  # atomic claim: two concurrent requests can never both submit
        update(Application).where(Application.id == app.id, Application.status == S.QUEUED.value)
        .values(status=S.APPLYING.value, updated_at=utcnow())
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise ServiceError(409, "Application is already being processed")
    app.status, app.job.status = S.APPLYING.value, S.APPLYING.value
    log_event(db, app, "APPLYING")
    db.commit()

    try:
        outcome = _execute(db, app, conn, profile, ai or get_ai_provider(), dry_run=False)
    except Exception as exc:  # noqa: BLE001
        log.exception("Application %s crashed", application_id)
        outcome = Outcome(S.FAILED, f"{type(exc).__name__}: {str(exc)[:200]}")
    finally:
        conn.close()

    app.failure_reason = None if outcome.status == S.APPLIED else outcome.reason
    if outcome.status == S.APPLIED:
        app.submitted_at, app.confirmation_text = utcnow(), outcome.confirmation
    transition(db, app, outcome.status, outcome.reason or outcome.confirmation or "")
    db.commit()
    _notify(db, app, notifier or get_notification_service())
    return app


def _notify(db: Session, app: Application, notifier: NotificationService) -> None:
    try:
        n = build_application_notification(app)
        notifier.send(n)
        log_event(db, app, "NOTIFIED", f"[{notifier.mode}] {n.subject}\n\n{n.body}")
    except Exception as exc:  # noqa: BLE001 - a notification failure never changes application status
        log.exception("Notification failed")
        log_event(db, app, "NOTIFICATION_FAILED", type(exc).__name__)
    db.commit()
