from typing import Any, Dict
from packages.llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    def draft_tailored_summary(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        skills = [s["name"] for s in candidate_profile.get("skills", [])][:5]
        skills_str = ", ".join(skills) if skills else "technical problem solving"
        
        job_title = job_data.get("title", "the role")
        company = job_data.get("company", "the team")

        projects = candidate_profile.get("projects", [])
        top_project = projects[0]["name"] if projects else "software development"

        return (
            f"Results-driven professional with hands-on expertise in {skills_str}. "
            f"Demonstrated ability delivering secure, reliable systems through key projects such as {top_project}. "
            f"Targeting {job_title} at {company} to contribute verified technical and security engineering capabilities."
        )

    def draft_cover_letter(self, candidate_profile: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        name = candidate_profile.get("name", "Candidate")
        job_title = job_data.get("title", "Position")
        company = job_data.get("company", "Hiring Team")
        
        skills = [s["name"] for s in candidate_profile.get("skills", [])][:6]
        skills_str = ", ".join(skills)

        projects = candidate_profile.get("projects", [])
        project_highlights = ""
        if projects:
            p = projects[0]
            project_highlights = f"For example, in project '{p['name']}', {p.get('description', '')}. "

        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong interest in the {job_title} position. "
            f"With a solid background in {skills_str}, I am excited about the opportunity to contribute to your engineering and security goals.\n\n"
            f"{project_highlights}"
            f"My technical work focuses on disciplined engineering, security best practices, and building robust systems. "
            f"I welcome the opportunity to discuss how my verified background aligns with the goals of {company}.\n\n"
            f"Sincerely,\n{name}"
        )

    def answer_application_question(
        self,
        question: str,
        candidate_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        q_lower = question.lower()
        skills = candidate_profile.get("skills", [])
        projects = candidate_profile.get("projects", [])
        work_auth = candidate_profile.get("work_authorization", "Authorized to work")

        if any(w in q_lower for w in ["authorization", "authorized", "visa", "sponsorship", "citizen", "eligible to work"]):
            return {
                "answer": f"{work_auth}. Does not require immediate sponsorship based on current profile.",
                "evidence": ["candidate.work_authorization"],
                "confidence": "high",
                "requires_review": True
            }

        if any(w in q_lower for w in ["salary", "compensation", "pay", "rate", "hourly"]):
            return {
                "answer": "Open to competitive market compensation commensurate with the position and responsibilities.",
                "evidence": ["candidate.work_preferences.salary"],
                "confidence": "medium",
                "requires_review": True
            }

        if any(w in q_lower for w in ["programming", "language", "code", "tech stack", "technologies", "skill"]):
            skill_names = [s["name"] for s in skills]
            evidence = [f"candidate.skill.{s['name']}" for s in skills[:3]]
            return {
                "answer": f"Core technical competencies include {', '.join(skill_names)} with practical application in production-ready projects.",
                "evidence": evidence,
                "confidence": "high",
                "requires_review": False
            }

        if any(w in q_lower for w in ["project", "portfolio", "achievement", "built", "experience"]):
            if projects:
                p = projects[0]
                return {
                    "answer": f"Developed '{p['name']}': {p.get('description', '')}. Technologies utilized: {', '.join(p.get('technologies', []))}.",
                    "evidence": [f"candidate.project.{p['name']}"],
                    "confidence": "high",
                    "requires_review": False
                }

        return {
            "answer": "Detail not explicitly specified in master candidate profile. Please input customized answer.",
            "evidence": [],
            "confidence": "low",
            "requires_review": True
        }
