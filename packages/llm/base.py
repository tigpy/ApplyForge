from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMProvider(ABC):
    @abstractmethod
    def draft_tailored_summary(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def draft_cover_letter(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def answer_application_question(
        self,
        question: str,
        candidate_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass
