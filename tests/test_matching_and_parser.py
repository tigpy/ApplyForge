"""
Tests for Deterministic Parser & Matching Engine
"""
from packages.matching.parser import parse_job_requirements
from packages.matching.engine import evaluate_match
from packages.domain.models import Job, JobRequirement, Candidate, Skill, Education, Project
from packages.domain.enums import RequirementType, SkillProficiency

def test_job_parser_extracts_skills_and_requirements():
    text = """
    We are seeking a Junior SOC Analyst with experience in Python, Wireshark, SIEM, and Splunk.
    Bachelor degree in Computer Science is required.
    """
    res = parse_job_requirements(text)
    skills = [r["normalized_skill"] for r in res if r["normalized_skill"]]
    assert "python" in skills
    assert "wireshark" in skills
    assert "splunk" in skills

def test_matching_engine_evaluates_candidate():
    cand = Candidate(
        name="Aryan Singh",
        email="aryan@example.com"
    )
    cand.skills = [
        Skill(name="Python", proficiency=SkillProficiency.ADVANCED),
        Skill(name="Wireshark", proficiency=SkillProficiency.INTERMEDIATE),
        Skill(name="Splunk", proficiency=SkillProficiency.INTERMEDIATE),
        Skill(name="Linux", proficiency=SkillProficiency.ADVANCED)
    ]
    cand.educations = [
        Education(degree="Bachelor of Science", field="Computer Science & Cybersecurity", institution="State Univ")
    ]
    cand.projects = [
        Project(name="Evidentia", description="Platform", technologies=["Python", "FastAPI"])
    ]
    
    job = Job(
        title="Junior SOC Analyst",
        company="SecuFirm",
        description_raw="Looking for SOC Analyst with Python, Wireshark, Splunk."
    )
    job.requirements = [
        JobRequirement(requirement_type=RequirementType.SKILL, text="Python", normalized_skill="python", mandatory=True),
        JobRequirement(requirement_type=RequirementType.SKILL, text="Wireshark", normalized_skill="wireshark", mandatory=True),
        JobRequirement(requirement_type=RequirementType.SKILL, text="Splunk", normalized_skill="splunk", mandatory=True)
    ]
    
    match_result = evaluate_match(cand, job)
    assert match_result["score"] >= 80.0
    assert len(match_result["strengths"]) == 3
    assert len(match_result["hard_gaps"]) == 0
