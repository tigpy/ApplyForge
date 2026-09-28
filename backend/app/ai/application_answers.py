"""Answering application questions strictly from stored facts. Unknown means unknown."""
import re

from pydantic import BaseModel, field_validator

ANSWER_PROMPT = (
    "Answer the application question using ONLY the provided facts. If the facts do not clearly contain "
    "the answer, return answer=null and confidence=0. Never guess or invent employers, degrees, "
    "certifications, dates, job titles, skills or achievements."
)
MIN_CONFIDENCE = 0.7
_BULKY_KEYS = {"skills", "education", "experience"}


class QuestionAnswer(BaseModel):
    answer: str | None
    confidence: float

    @field_validator("confidence")
    @classmethod
    def _clamp(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


def _stems(text: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z]+", text.lower())}


def mock_answer(question: str, facts: dict[str, str]) -> QuestionAnswer:
    """Match a fact key (e.g. work_authorization) against the question words. Never guesses."""
    q = _stems(question)
    for key, value in facts.items():
        stems = _stems(key.replace("_", " "))
        if key not in _BULKY_KEYS and stems and stems <= q and value:
            return QuestionAnswer(answer=str(value), confidence=0.9)
    return QuestionAnswer(answer=None, confidence=0.0)


def accept_answer(result: QuestionAnswer, options: list[str] | None = None) -> str | None:
    """Business-rule validation applied to every AI answer before it is used."""
    if not result.answer or result.confidence < MIN_CONFIDENCE:
        return None
    if options:
        by_lower = {o.lower(): o for o in options}
        return by_lower.get(result.answer.lower())
    return result.answer
