"""
OpenAI Provider with Structured Outputs and Anti-Hallucination Guardrails for ApplyForge
"""
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.llm.base import LLMProvider
from packages.llm.mock_provider import MockLLMProvider
from packages.shared.config import settings
from packages.shared.logger import logger
from packages.shared.security import wrap_untrusted_job_content

class RequirementItem(BaseModel):
    requirement_type: str = Field(description="skill, education, certification, or experience")
    text: str
    normalized_skill: Optional[str] = None
    mandatory: bool = True
    evidence: List[str] = Field(default_factory=list)

class StructuredJobRequirements(BaseModel):
    requirements: List[RequirementItem]

class GroundedAnswerItem(BaseModel):
    question: str
    draft_answer: str
    evidence_source: str
    verified_ground_truth: bool

class StructuredAnswers(BaseModel):
    answers: List[GroundedAnswerItem]

class StructuredMatchOutput(BaseModel):
    score: float
    required_coverage: float
    preferred_coverage: float
    explanation: str
    strengths: List[str]
    hard_gaps: List[str]
    uncertainties: List[str]

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.mock_fallback = MockLLMProvider()
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def _get_client(self):
        if not self.api_key:
            return None
        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        except ImportError:
            logger.warning("openai package not installed or configured, falling back to mock")
            return None

    def draft_tailored_summary(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        client = self._get_client()
        if not client:
            return self.mock_fallback.draft_tailored_summary(candidate_profile, job_data)

        delimited_job = wrap_untrusted_job_content(job_data.get("description_raw", ""))
        system_prompt = (
            "You are a truthful career assistant. You must ONLY use the provided candidate facts. "
            "NEVER invent skills, employers, metrics, or experiences."
        )
        user_prompt = f"Candidate Profile:\n{json.dumps(candidate_profile)}\n\nJob Posting:\n{delimited_job}\n\nDraft a concise, professional 3-sentence summary."
        
        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error in draft_tailored_summary: {e}")
            return self.mock_fallback.draft_tailored_summary(candidate_profile, job_data)

    def draft_cover_letter(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        client = self._get_client()
        if not client:
            return self.mock_fallback.draft_cover_letter(candidate_profile, job_data)

        delimited_job = wrap_untrusted_job_content(job_data.get("description_raw", ""))
        system_prompt = (
            "You are a professional cover letter assistant. Use ONLY candidate ground truth facts. "
            "Never invent facts or certifications."
        )
        user_prompt = f"Candidate Profile:\n{json.dumps(candidate_profile)}\n\nJob Posting:\n{delimited_job}\n\nDraft a tailored 3-paragraph cover letter."
        
        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error in draft_cover_letter: {e}")
            return self.mock_fallback.draft_cover_letter(candidate_profile, job_data)

    def answer_application_question(
        self,
        question: str,
        candidate_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        client = self._get_client()
        if not client:
            return self.mock_fallback.answer_application_question(question, candidate_profile, job_data)

        system_prompt = (
            "You are a ground-truth application assistant. Answer strictly using candidate facts. "
            "Never invent qualifications or answers."
        )
        user_prompt = f"Candidate Profile:\n{json.dumps(candidate_profile)}\n\nJob Data:\n{json.dumps(job_data)}\n\nQuestion:\n{question}\nProvide answer, evidence list, and confidence."

        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            return {
                "answer": resp.choices[0].message.content.strip(),
                "evidence": ["candidate_profile"],
                "confidence": "high",
                "requires_review": False
            }
        except Exception as e:
            logger.error(f"OpenAI answer_application_question error: {e}")
            return self.mock_fallback.answer_application_question(question, candidate_profile, job_data)

    def extract_structured_requirements(self, job_description: str) -> List[Dict[str, Any]]:
        client = self._get_client()
        if not client:
            from packages.matching.parser import parse_job_requirements
            return parse_job_requirements(job_description)

        try:
            delimited = wrap_untrusted_job_content(job_description)
            completion = client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract technical and educational requirements strictly as structured items."},
                    {"role": "user", "content": delimited}
                ],
                response_format=StructuredJobRequirements
            )
            parsed = completion.choices[0].message.parsed
            return [r.model_dump() for r in parsed.requirements]
        except Exception as e:
            logger.error(f"OpenAI structured extraction failed: {e}")
            from packages.matching.parser import parse_job_requirements
            return parse_job_requirements(job_description)
