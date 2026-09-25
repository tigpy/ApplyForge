import uuid
from typing import Any, Dict, List, Optional
from packages.connectors.base import ApplicationConnector
from packages.domain.enums import EmploymentType, WorkMode

class MockApplicationConnector(ApplicationConnector):
    name: str = "mock"

    def health_check(self) -> bool:
        return True

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return [
            {
                "external_id": "MOCK-101",
                "title": "Junior Cybersecurity Analyst",
                "company": "SecureNet Global",
                "location": "Remote",
                "work_mode": WorkMode.REMOTE,
                "employment_type": EmploymentType.FULL_TIME,
                "description_raw": (
                    "We are seeking a Junior Cybersecurity Analyst with experience in Python, "
                    "incident response, SIEM monitoring, and network security. "
                    "Must have bachelor's degree in Computer Science or related field. "
                    "Familiarity with SOC environments is a plus."
                )
            },
            {
                "external_id": "MOCK-102",
                "title": "Backend Python Engineer",
                "company": "CloudScale Systems",
                "location": "Remote",
                "work_mode": WorkMode.REMOTE,
                "employment_type": EmploymentType.FULL_TIME,
                "description_raw": (
                    "Looking for a Backend Python Engineer proficient in FastAPI, PostgreSQL, "
                    "Docker, and Redis. Experience with REST APIs, security best practices, and CI/CD required."
                )
            }
        ]

    def get_job(self, external_id: str) -> Optional[Dict[str, Any]]:
        jobs = self.search("")
        for j in jobs:
            if j["external_id"] == external_id:
                return j
        return None

    def normalize(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_id": raw_job.get("external_id", str(uuid.uuid4())),
            "url": raw_job.get("url", "https://example.com/jobs/mock"),
            "title": raw_job.get("title", "Mock Title"),
            "company": raw_job.get("company", "Mock Company"),
            "location": raw_job.get("location", "Remote"),
            "work_mode": raw_job.get("work_mode", WorkMode.REMOTE),
            "employment_type": raw_job.get("employment_type", EmploymentType.FULL_TIME),
            "description_raw": raw_job.get("description_raw", ""),
            "description_normalized": raw_job.get("description_raw", "").strip(),
            "duplicate_fingerprint": f"mockcompany::mocktitle::{raw_job.get('external_id')}"
        }

    def prepare_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "questions": [
                {
                    "question": "What is your primary programming language and cybersecurity experience?",
                    "requires_review": True
                },
                {
                    "question": "Are you legally authorized to work in the country for this position?",
                    "requires_review": True
                },
                {
                    "question": "Will you now or in the future require visa sponsorship?",
                    "requires_review": True
                }
            ],
            "required_documents": ["resume", "cover_letter"]
        }

    def submit_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "external_application_id": f"MOCK-SUBMIT-{uuid.uuid4().hex[:8].upper()}",
            "confirmation_message": "Application submitted successfully to Mock sandbox."
        }
