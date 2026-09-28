"""Hybrid matching: deterministic skill overlap + AI semantic score, across ALL resumes."""
import logging
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.ai.client import AIProvider, get_ai_provider
from app.ai.matching import SemanticMatch
from app.config import settings
from app.errors import ServiceError
from app.models import Job, MatchResult, Recommendation, Resume
from app.schemas import MatchResultData, ResumeScore
from app.services.resume_service import ResumeRepository
from app.skills import find_skills

log = logging.getLogger(__name__)
AI_WEIGHT = 0.3


def deterministic_score(job: Job, resume_text: str) -> tuple[int, list[str], list[str]]:
    """Returns (score 0-100, matched skills, missing skills). Evidence = literal skill terms in the resume."""
    required = find_skills(" ".join(job.requirements or [])) or find_skills(job.description)
    if not required:
        return 50, [], []
    have = find_skills(resume_text)
    matched, missing = sorted(required & have), sorted(required - have)
    return round(100 * len(matched) / len(required)), matched, missing


class ResumeMatcher(ABC):
    @abstractmethod
    def match(self, job: Job, resumes: list[Resume]) -> MatchResultData: ...


class HybridResumeMatcher(ResumeMatcher):
    def __init__(self, ai: AIProvider, threshold: int):
        self.ai, self.threshold = ai, threshold

    def match(self, job: Job, resumes: list[Resume]) -> MatchResultData:
        job_text = f"{job.title}\n{job.description}\n" + "\n".join(job.requirements or [])
        scored = []
        for r in resumes:
            det, matched, missing = deterministic_score(job, r.extracted_text)
            try:
                sem = self.ai.semantic_match(job_text, r.extracted_text)
            except Exception:  # noqa: BLE001 - AI outage must not stop the pipeline
                log.exception("AI semantic match failed; using deterministic score only")
                sem = SemanticMatch(score=det, reasons=["AI unavailable; deterministic score only"])
            final = round((1 - AI_WEIGHT) * det + AI_WEIGHT * sem.score)
            scored.append((final, r, det, matched, missing, sem))
        final, best, det, matched, missing, sem = max(scored, key=lambda s: (s[0], -s[1].id))
        return MatchResultData(
            job_id=job.id,
            selected_resume_id=best.id,
            score=final,
            strengths=[f"Resume shows: {m}" for m in matched],
            missing_requirements=missing,
            reasons=[f"Skill match {det}% (deterministic)", f"Semantic score {sem.score} ({self.ai.name})", *sem.reasons],
            recommendation=Recommendation.APPLY if final >= self.threshold else Recommendation.SKIP,
            resume_scores=[ResumeScore(resume_id=s[1].id, resume_name=s[1].filename, score=s[0]) for s in scored],
        )


def run_match(db: Session, job: Job, ai: AIProvider | None = None) -> MatchResult:
    """Match a job against every stored resume, persist the result, and register the application."""
    from app.services.application_service import register_match  # local import avoids a cycle

    resumes = ResumeRepository(db).list()
    if not resumes:
        raise ServiceError(409, "Upload at least one resume before matching")
    data = HybridResumeMatcher(ai or get_ai_provider(), settings.match_threshold).match(job, resumes)
    row = MatchResult(
        job_id=job.id, selected_resume_id=data.selected_resume_id, score=data.score, strengths=data.strengths,
        missing_requirements=data.missing_requirements, reasons=data.reasons,
        recommendation=data.recommendation.value, resume_scores=[s.model_dump() for s in data.resume_scores],
    )
    db.add(row)
    register_match(db, job, row)
    db.commit()
    return row
