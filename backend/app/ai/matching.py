"""Structured schemas, prompts and mock logic for requirement extraction and semantic matching."""
import re

from pydantic import BaseModel, field_validator

from app.skills import find_skills

REQUIREMENTS_PROMPT = (
    "Extract the job requirements stated in the text. Return only requirements that are explicitly "
    "written; do not add, infer or embellish anything."
)
SEMANTIC_MATCH_PROMPT = (
    "Score 0-100 how well the resume fits the job. Use ONLY facts written in the resume text. "
    "Never assume or invent experience, skills, employers, degrees, certifications or dates. "
    "Give short reasons that refer to evidence in the resume."
)


class RequirementExtraction(BaseModel):
    requirements: list[str]


class SemanticMatch(BaseModel):
    score: int
    reasons: list[str]

    @field_validator("score")
    @classmethod
    def _clamp(cls, v: int) -> int:
        return max(0, min(100, v))


_STOP = {"the", "and", "for", "with", "you", "are", "our", "will", "have", "this", "that", "from", "your",
         "who", "join", "team", "role", "work", "using", "experience", "requirements"}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9+#]{2,}", text.lower()) if w not in _STOP}


def mock_extract_requirements(description: str) -> RequirementExtraction:
    bullets = [m.strip() for m in re.findall(r"^\s*[-*\u2022]\s+(.+)$", description, re.M)]
    return RequirementExtraction(requirements=bullets or sorted(find_skills(description)))


def mock_semantic_match(job_text: str, resume_text: str) -> SemanticMatch:
    job_t, resume_t = _tokens(job_text), _tokens(resume_text)
    if not job_t:
        return SemanticMatch(score=0, reasons=["Job text is empty"])
    overlap = job_t & resume_t
    score = min(100, round(200 * len(overlap) / len(job_t)))
    return SemanticMatch(score=score, reasons=[f"{len(overlap)} of {len(job_t)} job terms appear in the resume (mock AI)"])
