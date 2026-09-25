import re
from typing import Any, Dict, List
from packages.domain.enums import RequirementType

COMMON_SKILLS = [
    "python", "javascript", "typescript", "golang", "go", "c++", "c", "rust",
    "java", "sql", "bash", "shell", "fastapi", "django", "flask", "postgresql",
    "postgres", "mysql", "mongodb", "redis", "rest api", "graphql", "microservices",
    "cybersecurity", "information security", "incident response", "siem", "splunk",
    "wireshark", "soc", "soc analyst", "threat intelligence", "penetration testing",
    "vulnerability management", "network security", "ids/ips", "owasp", "snort",
    "edr", "endpoint security", "malware analysis", "forensics", "mitre att&ck",
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "linux",
    "ci/cd", "github actions", "gitlab ci", "ansible", "cloud security"
]

COMMON_CERTS = [
    "comptia security+", "security+", "cissp", "ceh", "certified ethical hacker",
    "cisa", "cism", "ccna", "network+", "aws certified", "cybops", "ejpt", "oscp"
]

def extract_requirements(job_description: str) -> List[Dict[str, Any]]:
    text_lower = job_description.lower()
    requirements: List[Dict[str, Any]] = []

    exp_pattern = re.compile(r'(\d+)\+?\s*(?:to\s*(\d+))?\s*(?:years|yrs)\b(?:\s*of)?(?:\s*(?:hands-on|professional|work|relevant))?\s*experience', re.IGNORECASE)
    for match in exp_pattern.finditer(job_description):
        full_match = match.group(0).strip()
        years = int(match.group(1))
        requirements.append({
            "requirement_type": RequirementType.EXPERIENCE,
            "text": full_match,
            "normalized_skill": f"{years}_years_experience",
            "mandatory": True,
            "evidence": [f"min_years:{years}"]
        })
        break

    if "bachelor" in text_lower or "degree in computer science" in text_lower or "b.s." in text_lower or "b.tech" in text_lower:
        requirements.append({
            "requirement_type": RequirementType.EDUCATION,
            "text": "Bachelor's degree in Computer Science, Cybersecurity, or related field",
            "normalized_skill": "bachelors_degree",
            "mandatory": "required" in text_lower or "must have" in text_lower,
            "evidence": ["education:bachelor"]
        })
    elif "master" in text_lower or "m.s." in text_lower:
        requirements.append({
            "requirement_type": RequirementType.EDUCATION,
            "text": "Master's degree in Computer Science or related field",
            "normalized_skill": "masters_degree",
            "mandatory": False,
            "evidence": ["education:master"]
        })

    for cert in COMMON_CERTS:
        pattern = r'\b' + re.escape(cert) + r'\b'
        if re.search(pattern, text_lower):
            requirements.append({
                "requirement_type": RequirementType.CERTIFICATION,
                "text": cert.title(),
                "normalized_skill": cert.replace(" ", "_"),
                "mandatory": "required" in text_lower and cert in text_lower,
                "evidence": [f"cert:{cert}"]
            })

    seen_skills = set()
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            if skill not in seen_skills:
                seen_skills.add(skill)
                is_mandatory = True
                idx = text_lower.find(skill)
                surrounding = text_lower[max(0, idx - 60): min(len(text_lower), idx + 60)]
                if "preferred" in surrounding or "nice to have" in surrounding or "plus" in surrounding:
                    is_mandatory = False

                requirements.append({
                    "requirement_type": RequirementType.SKILL,
                    "text": skill.title(),
                    "normalized_skill": skill.replace(" ", "_"),
                    "mandatory": is_mandatory,
                    "evidence": [f"skill:{skill}"]
                })

    return requirements

parse_job_requirements = extract_requirements
