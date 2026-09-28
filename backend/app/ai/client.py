"""Thin AI abstraction: AIProvider -> OpenAIProvider | MockAIProvider. Structured outputs only."""
from abc import ABC, abstractmethod
from functools import lru_cache

from app.ai.application_answers import ANSWER_PROMPT, QuestionAnswer, mock_answer
from app.ai.matching import (
    REQUIREMENTS_PROMPT,
    SEMANTIC_MATCH_PROMPT,
    RequirementExtraction,
    SemanticMatch,
    mock_extract_requirements,
    mock_semantic_match,
)
from app.config import settings

_MAX_CHARS = 12000


class AIProvider(ABC):
    name: str

    @abstractmethod
    def extract_requirements(self, description: str) -> RequirementExtraction: ...

    @abstractmethod
    def semantic_match(self, job_text: str, resume_text: str) -> SemanticMatch: ...

    @abstractmethod
    def answer_question(self, question: str, facts: dict[str, str]) -> QuestionAnswer: ...


class MockAIProvider(AIProvider):
    """Deterministic, offline. Used when no API key is configured and in tests."""

    name = "mock"

    def extract_requirements(self, description: str) -> RequirementExtraction:
        return mock_extract_requirements(description)

    def semantic_match(self, job_text: str, resume_text: str) -> SemanticMatch:
        return mock_semantic_match(job_text, resume_text)

    def answer_question(self, question: str, facts: dict[str, str]) -> QuestionAnswer:
        return mock_answer(question, facts)


class OpenAIProvider(AIProvider):
    """Structured outputs via Pydantic schemas. NOT exercised by the test suite (needs a real key)."""

    name = "openai"

    def __init__(self, api_key: str, model: str):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def _parse(self, system: str, user: str, schema):
        completion = self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user[:_MAX_CHARS]}],
            response_format=schema,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("Model returned no structured output")
        return parsed

    def extract_requirements(self, description: str) -> RequirementExtraction:
        return self._parse(REQUIREMENTS_PROMPT, description, RequirementExtraction)

    def semantic_match(self, job_text: str, resume_text: str) -> SemanticMatch:
        user = f"JOB:\n{job_text[:_MAX_CHARS // 2]}\n\nRESUME:\n{resume_text[:_MAX_CHARS // 2]}"
        return self._parse(SEMANTIC_MATCH_PROMPT, user, SemanticMatch)

    def answer_question(self, question: str, facts: dict[str, str]) -> QuestionAnswer:
        facts_text = "\n".join(f"{k}: {v}" for k, v in facts.items())
        return self._parse(ANSWER_PROMPT, f"FACTS:\n{facts_text}\n\nQUESTION:\n{question}", QuestionAnswer)


@lru_cache
def get_ai_provider() -> AIProvider:
    mode = settings.ai_provider.lower()
    if mode == "openai" or (mode == "auto" and settings.openai_api_key):
        if not settings.openai_api_key:
            raise RuntimeError("AI_PROVIDER=openai requires OPENAI_API_KEY")
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return MockAIProvider()
