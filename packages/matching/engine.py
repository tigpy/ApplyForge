from typing import Any, Dict
from packages.domain.enums import MatchStatus, RequirementType
from packages.domain.models import Candidate, Job

TRANSFERABLE_MAP = {
    "fastapi": ["python", "rest_api"],
    "flask": ["python", "rest_api"],
    "django": ["python", "rest_api"],
    "postgres": ["postgresql", "sql"],
    "postgresql": ["sql"],
    "mysql": ["sql"],
    "bash": ["linux", "shell"],
    "k8s": ["kubernetes", "docker"],
    "siem": ["splunk", "soc"],
    "soc_analyst": ["soc", "incident_response"],
    "endpoint_security": ["edr", "incident_response"],
}

def evaluate_match(candidate: Candidate, job: Job) -> Dict[str, Any]:
    candidate_skills = {s.name.lower().replace(" ", "_"): s for s in candidate.skills}
    candidate_project_tech = set()
    for p in candidate.projects:
        for t in (p.technologies or []):
            candidate_project_tech.add(t.lower().replace(" ", "_"))

    required_items = [r for r in job.requirements if r.mandatory]
    preferred_items = [r for r in job.requirements if not r.mandatory]

    strengths = []
    hard_gaps = []
    uncertainties = []

    matched_required = 0
    for req in required_items:
        norm_key = (req.normalized_skill or req.text).lower()
        if norm_key in candidate_skills:
            matched_required += 1
            evidence_item = [f"skill:{candidate_skills[norm_key].name}"]
            for p in candidate.projects:
                if any(t.lower().replace(" ", "_") == norm_key for t in (p.technologies or [])):
                    evidence_item.append(f"project:{p.name}")
            strengths.append({
                "requirement": req.text,
                "status": MatchStatus.STRONG.value,
                "evidence": evidence_item
            })
        elif norm_key in candidate_project_tech:
            matched_required += 1
            strengths.append({
                "requirement": req.text,
                "status": MatchStatus.STRONG.value,
                "evidence": [f"project_tech:{norm_key}"]
            })
        elif req.requirement_type == RequirementType.EDUCATION:
            if candidate.educations:
                matched_required += 1
                strengths.append({
                    "requirement": req.text,
                    "status": MatchStatus.STRONG.value,
                    "evidence": [f"education:{candidate.educations[0].degree} in {candidate.educations[0].field}"]
                })
            else:
                hard_gaps.append({
                    "requirement": req.text,
                    "status": MatchStatus.MISSING.value,
                    "detail": "Candidate has no education recorded"
                })
        elif req.requirement_type == RequirementType.EXPERIENCE:
            total_exp = len(candidate.experiences)
            if total_exp > 0:
                strengths.append({
                    "requirement": req.text,
                    "status": MatchStatus.TRANSFERABLE.value,
                    "evidence": [f"experience:{e.title} at {e.organization}" for e in candidate.experiences]
                })
                matched_required += 0.8
            else:
                uncertainties.append(f"Experience requirement verification needed: {req.text}")
        else:
            transferable = False
            for trans_key, related in TRANSFERABLE_MAP.items():
                if norm_key == trans_key or norm_key in related:
                    for rel in related:
                        if rel in candidate_skills or rel in candidate_project_tech:
                            matched_required += 0.7
                            transferable = True
                            strengths.append({
                                "requirement": req.text,
                                "status": MatchStatus.TRANSFERABLE.value,
                                "evidence": [f"transferable_skill:{rel}"]
                            })
                            break
                if transferable:
                    break

            if not transferable:
                hard_gaps.append({
                    "requirement": req.text,
                    "status": MatchStatus.MISSING.value,
                    "detail": "No direct or transferable evidence in candidate profile"
                })

    matched_preferred = 0
    for req in preferred_items:
        norm_key = (req.normalized_skill or req.text).lower()
        if norm_key in candidate_skills or norm_key in candidate_project_tech:
            matched_preferred += 1
            strengths.append({
                "requirement": f"(Preferred) {req.text}",
                "status": MatchStatus.STRONG.value,
                "evidence": [f"skill:{norm_key}"]
            })

    req_coverage = (matched_required / len(required_items) * 100.0) if required_items else 100.0
    pref_coverage = (matched_preferred / len(preferred_items) * 100.0) if preferred_items else 100.0

    base_score = (req_coverage * 0.7) + (pref_coverage * 0.3)
    penalty = min(30.0, len(hard_gaps) * 10.0)
    final_score = max(0.0, min(100.0, base_score - penalty))

    if "sponsorship" in (job.description_raw or "").lower():
        uncertainties.append("Job description mentions visa sponsorship; verify candidate eligibility.")

    explanation_lines = [
        f"Match Score: {round(final_score, 1)}% (Required Coverage: {round(req_coverage, 1)}%, Preferred Coverage: {round(pref_coverage, 1)}%).",
        f"Key Strengths ({len(strengths)} matched requirements): {', '.join([s['requirement'] for s in strengths[:5]])}.",
    ]
    if hard_gaps:
        explanation_lines.append(f"Gaps identified ({len(hard_gaps)} missing): {', '.join([g['requirement'] for g in hard_gaps])}.")
    if uncertainties:
        explanation_lines.append(f"Uncertainties to confirm: {'; '.join(uncertainties)}.")

    return {
        "score": round(final_score, 1),
        "required_coverage": round(req_coverage, 1),
        "preferred_coverage": round(pref_coverage, 1),
        "strengths": strengths,
        "hard_gaps": hard_gaps,
        "uncertainties": uncertainties,
        "explanation": "\n".join(explanation_lines)
    }
