import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

from packages.domain.models import Candidate, Job, Resume
from packages.shared.config import settings

def sanitize_filename_part(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '', text.replace(" ", "-"))

def generate_resume_pdf(
    candidate: Candidate,
    job: Job,
    resume: Optional[Resume],
    tailored_data: Dict[str, Any]
) -> str:
    candidate_name = sanitize_filename_part(candidate.name)
    family_name = sanitize_filename_part(resume.job_family if resume else "General")
    company_name = sanitize_filename_part(job.company or "Company")
    year = datetime.now().year

    filename = f"{candidate_name}_Resume_{family_name}_{company_name}_{year}.pdf"
    output_dir = settings.storage_path / "resumes"
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4,
        alignment=1
    )

    contact_style = ParagraphStyle(
        'ContactInfo',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4,
        fontName="Helvetica-Bold"
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=15,
        spaceAfter=3
    )

    elements = []

    # 1. Header
    elements.append(Paragraph(candidate.name, title_style))
    contact_parts = [p for p in [candidate.email, candidate.phone, candidate.location] if p]
    elements.append(Paragraph(" • ".join(contact_parts), contact_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # 2. Summary
    summary_text = tailored_data.get("tailored_summary") or candidate.summary or ""
    if summary_text:
        elements.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
        elements.append(Paragraph(summary_text, body_style))
        elements.append(Spacer(1, 4))

    # 3. Skills
    ordered_skills = tailored_data.get("ordered_skills", [])
    if ordered_skills:
        elements.append(Paragraph("CORE SKILLS & TECHNOLOGIES", section_heading))
        skills_by_cat: Dict[str, List[str]] = {}
        for s in ordered_skills:
            cat = s.get("category", "Technical")
            skills_by_cat.setdefault(cat, []).append(s["name"])
        
        for cat, sk_list in skills_by_cat.items():
            elements.append(Paragraph(f"<b>{cat}:</b> {', '.join(sk_list)}", bullet_style))
        elements.append(Spacer(1, 4))

    # 4. Experience
    if candidate.experiences:
        elements.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
        for exp in candidate.experiences:
            period = f"{exp.start_date or ''} – {exp.end_date or 'Present'}"
            header_line = f"<b>{exp.title}</b> | {exp.organization} <font color='#64748B'>({period})</font>"
            elements.append(Paragraph(header_line, body_style))
            elements.append(Paragraph(f"• {exp.description}", bullet_style))
            elements.append(Spacer(1, 4))

    # 5. Projects
    projects = tailored_data.get("ordered_projects", [])
    if projects:
        elements.append(Paragraph("TECHNICAL PROJECTS", section_heading))
        for proj in projects[:3]:
            tech_str = ", ".join(proj.get("technologies", []))
            p_header = f"<b>{proj['name']}</b> | <font color='#0284C7'>{tech_str}</font>"
            elements.append(Paragraph(p_header, body_style))
            elements.append(Paragraph(f"• {proj['description']}", bullet_style))
            elements.append(Spacer(1, 4))

    # 6. Education & Certs
    if candidate.educations or candidate.certifications:
        elements.append(Paragraph("EDUCATION & CERTIFICATIONS", section_heading))
        for edu in candidate.educations:
            elements.append(Paragraph(f"<b>{edu.degree} in {edu.field}</b> – {edu.institution} ({edu.start_date} – {edu.end_date})", bullet_style))
        for cert in candidate.certifications:
            elements.append(Paragraph(f"<b>{cert.name}</b> – {cert.issuer} ({cert.status})", bullet_style))

    # 7. Provenance Footer
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=4))
    footer_text = (
        f"<font size='7' color='#94A3B8'>Tailored for Job #{job.id} ({job.company} - {job.title}) • "
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} • Grounded in master profile</font>"
    )
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', alignment=1)))

    doc.build(elements)
    return str(filepath)
