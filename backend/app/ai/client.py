"""Thin AI abstraction: AIProvider -> OpenAIProvider | MockAIProvider. Structured outputs only."""
import logging
from abc import ABC, abstractmethod
from functools import lru_cache

log = logging.getLogger(__name__)

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


class GeminiProvider(AIProvider):
    """Google Gemini AI via OpenAI-compatible endpoint with automatic fallback."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite"):
        from openai import OpenAI

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self._model = model or "gemini-3.5-flash-lite"
        self._mock = MockAIProvider()
        self._cache: dict[tuple[str, str, str], object] = {}

    def _parse(self, system: str, user: str, schema):
        cache_key = (system, user[:_MAX_CHARS], schema.__name__)
        if cache_key in self._cache:
            return self._cache[cache_key]

        models_to_try = [self._model]
        for alt in ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite"):
            if alt not in models_to_try:
                models_to_try.append(alt)

        for candidate_model in models_to_try:
            try:
                completion = self._client.beta.chat.completions.parse(
                    model=candidate_model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user[:_MAX_CHARS]}],
                    response_format=schema,
                )
                parsed = completion.choices[0].message.parsed
                if parsed is not None:
                    if candidate_model != self._model:
                        log.info("Gemini switched active model from %s to working model %s", self._model, candidate_model)
                        self._model = candidate_model
                    if len(self._cache) > 1000:
                        self._cache.clear()
                    self._cache[cache_key] = parsed
                    return parsed
            except Exception as exc:
                log.warning("Gemini model %s failed (%s); trying fallback", candidate_model, exc)

        return None

    def extract_requirements(self, description: str) -> RequirementExtraction:
        res = self._parse(REQUIREMENTS_PROMPT, description, RequirementExtraction)
        return res if res is not None else self._mock.extract_requirements(description)

    def semantic_match(self, job_text: str, resume_text: str) -> SemanticMatch:
        user = f"JOB:\n{job_text[:_MAX_CHARS // 2]}\n\nRESUME:\n{resume_text[:_MAX_CHARS // 2]}"
        res = self._parse(SEMANTIC_MATCH_PROMPT, user, SemanticMatch)
        return res if res is not None else self._mock.semantic_match(job_text, resume_text)

    def answer_question(self, question: str, facts: dict[str, str]) -> QuestionAnswer:
        facts_text = "\n".join(f"{k}: {v}" for k, v in facts.items())
        res = self._parse(ANSWER_PROMPT, f"FACTS:\n{facts_text}\n\nQUESTION:\n{question}", QuestionAnswer)
        return res if res is not None else self._mock.answer_question(question, facts)


@lru_cache
def get_ai_provider() -> AIProvider:
    mode = settings.ai_provider.lower()
    gemini_key = settings.gemini_api_key or (
        settings.openai_api_key if settings.openai_api_key.startswith(("AQ.", "AIza")) else ""
    )
    openai_key = settings.openai_api_key if not settings.openai_api_key.startswith(("AQ.", "AIza")) else ""

    if mode in ("gemini", "google") or (mode == "auto" and gemini_key):
        if not gemini_key:
            raise RuntimeError("AI_PROVIDER=gemini requires GEMINI_API_KEY (or Gemini key in OPENAI_API_KEY)")
        return GeminiProvider(gemini_key, settings.gemini_model)

    if mode == "openai" or (mode == "auto" and openai_key):
        if not openai_key:
            raise RuntimeError("AI_PROVIDER=openai requires OPENAI_API_KEY")
        return OpenAIProvider(openai_key, settings.openai_model)

    return MockAIProvider()
