"""
LaTeX to PDF Rendering Service for ApplyForge
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from packages.shared.logger import logger
from packages.domain.models import Candidate, Resume

class LatexResumeRenderer:
    @staticmethod
    def generate_latex_source(candidate: Candidate, resume: Optional[Resume] = None) -> str:
        """Generates standard ATS-friendly LaTeX template source."""
        name = candidate.name or "Candidate"
        email = candidate.email or ""
        phone = candidate.phone or ""
        location = candidate.location or ""
        summary = candidate.summary or ""

        latex = f"""\\documentclass[letterpaper,10pt]{{article}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{hyperref}}
\\usepackage{{enumitem}}

\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-0.5in}}
\\addtolength{{\\textheight}}{{1.0in}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

\\begin{{document}}

\\begin{{center}}
    {{\\Huge \\scshape {name}}} \\\\
    \\vspace{{2pt}}
    \\small {phone} $|$ \\href{{mailto:{email}}}{{{email}}} $|$ {location}
\\end{{center}}

\\section*{{Professional Summary}}
{summary}

\\section*{{Education}}
\\begin{{itemize}}[leftmargin=*]
"""
        for edu in (candidate.educations or []):
            latex += f"\\item \\textbf{{{edu.institution}}} --- {edu.degree} in {edu.field} ({edu.start_date or ''} - {edu.end_date or ''})\n"

        latex += """\\end{itemize}

\\section*{Technical Skills}
\\begin{itemize}[leftmargin=*]
"""
        skill_names = [s.name for s in (candidate.skills or [])]
        latex += f"\\item \\textbf{{Core Technologies:}} {', '.join(skill_names)}\n"
        latex += """\\end{itemize}

\\section*{Experience & Projects}
\\begin{itemize}[leftmargin=*]
"""
        for exp in (candidate.experiences or []):
            latex += f"\\item \\textbf{{{exp.organization}}} --- {exp.title} ({exp.start_date or ''} - {exp.end_date or ''})\\\\ {exp.description}\n"
        for proj in (candidate.projects or []):
            latex += f"\\item \\textbf{{{proj.name}}}: {proj.description} \\\\ \\textit{{Tech: {', '.join(proj.technologies or [])}}}\n"

        latex += """\\end{itemize}

\\end{document}
"""
        return latex

    @classmethod
    def render_pdf(cls, latex_source: str, output_path: str) -> bool:
        """Attempts pdflatex compilation, or returns False if pdflatex is not installed."""
        pdflatex_bin = shutil.which("pdflatex")
        if not pdflatex_bin:
            logger.info("pdflatex executable not found in PATH; LaTeX source preserved")
            return False

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "resume.tex"
            tex_file.write_text(latex_source, encoding="utf-8")
            try:
                res = subprocess.run(
                    [pdflatex_bin, "-interaction=nonstopmode", "resume.tex"],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30
                )
                built_pdf = Path(tmpdir) / "resume.pdf"
                if built_pdf.exists():
                    shutil.copy(str(built_pdf), output_path)
                    return True
            except Exception as e:
                logger.error(f"LaTeX compile failed: {e}")
                return False
        return False
