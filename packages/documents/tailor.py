from typing import Any, Dict, List, Optional
from packages.domain.models import Candidate, Job, Resume
from packages.llm.base import LLMProvider

def select_best_resume_variant(candidate: Candidate, job: Job) -> Optional[Resume]:
    title_lower = (job.title or "").lower()
    desc_lower = (job.description_raw or "").lower()

    target_family = "General"
    if any(k in title_lower or k in desc_lower for k in ["soc", "security", "incident", "siem", "cyber", "threat"]):
        target_family = "Cybersecurity"
    elif any(k in title_lower or k in desc_lower for k in ["backend", "python", "api", "engineer"]):
        target_family = "Backend"
    elif any(k in title_lower or k in desc_lower for k in ["cloud", "devops", "kubernetes", "docker", "infra"]):
        target_family = "Cloud/DevOps"

    for r in candidate.resumes:
        if r.job_family.lower() == target_family.lower():
            return r

    return candidate.resumes[0] if candidate.resumes else None

def tailor_candidate_materials(
    candidate: Candidate,
    job: Job,
    resume: Optional[Resume],
    llm: LLMProvider
) -> Dict[str, Any]:
    job_skills = set()
    for req in job.requirements:
        if req.normalized_skill:
            job_skills.add(req.normalized_skill.lower().replace("_", " "))

    matched_skills = []
    other_skills = []
    for s in candidate.skills:
        skill_dict = {"name": s.name, "category": s.category, "proficiency": s.proficiency.value}
        if s.name.lower() in job_skills or any(js in s.name.lower() for js in job_skills):
            matched_skills.append(skill_dict)
        else:
            other_skills.append(skill_dict)
    ordered_skills = matched_skills + other_skills

    ordered_projects = []
    for p in candidate.projects:
        tech_set = {t.lower() for t in (p.technologies or [])}
        score = len(tech_set.intersection(job_skills))
        ordered_projects.append((score, {
            "name": p.name,
            "description": p.description,
            "technologies": p.technologies,
            "url": p.url,
            "evidence": p.evidence
        }))
    ordered_projects.sort(key=lambda x: x[0], reverse=True)
    sorted_projects = [p[1] for p in ordered_projects]

    candidate_dict = {
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "work_authorization": candidate.work_authorization,
        "skills": ordered_skills,
        "projects": sorted_projects,
        "summary": candidate.summary,
        "work_preferences": candidate.work_preferences
    }

    job_dict = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description_raw": job.description_raw
    }

    tailored_summary = llm.draft_tailored_summary(candidate_dict, job_dict)
    cover_letter = llm.draft_cover_letter(candidate_dict, job_dict)

    return {
        "resume_variant_id": resume.id if resume else None,
        "resume_variant_name": resume.name if resume else "Master Profile",
        "tailored_summary": tailored_summary,
        "ordered_skills": ordered_skills,
        "ordered_projects": sorted_projects,
        "cover_letter": cover_letter
    }
