"""
Tests for Document Extraction and LaTeX Resume Generation
"""
import os
import tempfile
from packages.documents.extractor import DocumentExtractor
from packages.documents.latex_renderer import LatexResumeRenderer
from packages.domain.models import Candidate, Skill
from packages.domain.enums import SkillProficiency
from packages.ai.openai_provider import OpenAIProvider

def test_latex_resume_rendering():
    cand = Candidate(
        name="Aryan Singh",
        email="aryan@example.com",
        phone="+1 555 019 2834",
        location="San Francisco, CA",
        summary="Security Engineer"
    )
    cand.skills = [Skill(name="Python", proficiency=SkillProficiency.ADVANCED)]
    latex_code = LatexResumeRenderer.generate_latex_source(cand)
    assert "\\Huge \\scshape Aryan Singh" in latex_code
    assert "Python" in latex_code

def test_document_extractor_plain_text():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("Resume content test")
        temp_path = f.name
    try:
        text = DocumentExtractor.extract_text(temp_path)
        assert "Resume content test" in text
    finally:
        os.remove(temp_path)

def test_openai_provider_fallback():
    provider = OpenAIProvider()
    summary = provider.draft_tailored_summary(
        {"name": "Aryan Singh", "skills": []},
        {"title": "Security Analyst", "description_raw": "Job description"}
    )
    assert len(summary) > 20
