"""
Tests for Resume Generation and Ground-Truth Tailoring
"""
import os
from packages.documents.tailor import select_best_resume_variant, tailor_candidate_materials
from packages.documents.pdf_generator import generate_resume_pdf
from packages.domain.models import Candidate, Job, Resume, Skill, Education, Project
from packages.domain.enums import SkillProficiency
from packages.llm.mock_provider import MockLLMProvider

def test_pdf_generation_produces_valid_pdf_file():
    cand = Candidate(
        name="Aryan Singh",
        email="aryan@example.com",
        phone="+1 555 019 2834",
        location="San Francisco, CA",
        summary="Security Engineer"
    )
    cand.skills = [Skill(name="Python", proficiency=SkillProficiency.ADVANCED)]
    cand.educations = [Education(degree="BS", field="CS", institution="Tech Univ", end_date="2024")]
    cand.projects = [Project(name="Evidentia", description="Project", technologies=["Python"])]
    cand.resumes = [Resume(name="Cybersecurity Resume", job_family="Cybersecurity")]
    
    job = Job(title="SOC Analyst", company="Acme Defense", description_raw="Cybersecurity role")
    llm = MockLLMProvider()
    tailored = tailor_candidate_materials(cand, job, cand.resumes[0], llm)
    
    pdf_path = generate_resume_pdf(cand, job, cand.resumes[0], tailored)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 500
