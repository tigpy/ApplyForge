"""Generate two small sample resume PDFs for local testing / the E2E fixture.

Usage (with backend venv active):  python scripts/make_sample_resumes.py [output_dir]
Default output: data/sample-resumes
"""
import sys
from pathlib import Path

import pymupdf

SAMPLES = {
    "cybersecurity.pdf": (
        "Aryan Sharma - Cybersecurity Analyst\n"
        "Email: aryan.sharma@example.com | Phone: +91 9876543210 | Location: Mumbai, India\n\n"
        "Summary:\nDedicated cybersecurity analyst with expertise in threat hunting, vulnerability assessment, and security monitoring.\n\n"
        "Skills:\nPython, Linux, SIEM, Splunk, Incident Response, Networking, TCP/IP, Wireshark, Log Analysis, "
        "Vulnerability Assessment, Firewall, Penetration Testing, OWASP.\n\n"
        "Experience:\n- Monitored security alerts in 24/7 SOC environment using Splunk and Wireshark.\n"
        "- Conducted vulnerability assessments and security patch audits.\n\n"
        "Education:\nB.Tech in Computer Science, 2024"
    ),
    "soc-analyst.pdf": (
        "Aryan Sharma - SOC Analyst\n"
        "Email: aryan.sharma@example.com | Phone: +91 9876543210 | Location: Mumbai, India\n\n"
        "Summary:\nSOC Analyst specializing in real-time incident detection, triage, and response.\n\n"
        "Skills:\nSIEM tools, Splunk, Log Analysis, Incident Response, Linux administration, Networking fundamentals, "
        "TCP/IP, Wireshark, MITRE ATT&CK framework, Python scripting.\n\n"
        "Experience:\n- Tier 1 SOC Analyst performing alert triage and incident response.\n"
        "- Developed automated log analysis scripts with Python and Linux bash.\n\n"
        "Education:\nB.Tech in Information Technology, 2024"
    ),
    "backend-developer.pdf": (
        "Aryan Sharma - Backend Python Developer\n"
        "Email: aryan.sharma@example.com | Phone: +91 9876543210 | Location: Mumbai, India\n\n"
        "Summary:\nBackend software engineer skilled in designing scalable APIs and database architectures.\n\n"
        "Skills:\nPython, FastAPI, Django, Flask, SQL, PostgreSQL, REST API design, Git, Docker, Linux.\n\n"
        "Experience:\n- Built production microservices and REST APIs using FastAPI and SQLAlchemy.\n"
        "- Optimized SQL queries and integrated relational databases.\n\n"
        "Education:\nB.Tech in Computer Science, 2024"
    ),
    "java-developer.pdf": (
        "Aryan Sharma - Java Developer\n"
        "Email: aryan.sharma@example.com | Phone: +91 9876543210 | Location: Mumbai, India\n\n"
        "Summary:\nJava software engineer proficient in modern enterprise Java and backend architectures.\n\n"
        "Skills:\nJava, Spring Boot, SQL, MySQL, REST API, Git, Linux, Docker, Microservices, Object-Oriented Design.\n\n"
        "Experience:\n- Developed enterprise REST services with Java and Spring.\n"
        "- Designed database schemas in MySQL.\n\n"
        "Education:\nB.Tech in Computer Science, 2024"
    ),
    "fresher-general.pdf": (
        "Aryan Sharma - Junior Software Developer\n"
        "Email: aryan.sharma@example.com | Phone: +91 9876543210 | Location: Mumbai, India\n\n"
        "Summary:\nMotivated software engineering graduate with hands-on coding foundation.\n\n"
        "Skills:\nPython, JavaScript, Git, Linux, SQL, HTML, CSS, Problem Solving, Data Analysis.\n\n"
        "Experience:\n- Academic projects in Python and web development.\n\n"
        "Education:\nB.Tech in Computer Science, 2025"
    ),
}


def main() -> None:
    targets = [
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "sample-resumes",
        Path(__file__).resolve().parents[1] / "resumes",
    ]
    for out in targets:
        out.mkdir(parents=True, exist_ok=True)
        for name, text in SAMPLES.items():
            doc = pymupdf.open()
            doc.new_page().insert_textbox(pymupdf.Rect(50, 50, 550, 780), text, fontsize=11)
            doc.save(out / name)
            doc.close()
            print("wrote", out / name)


if __name__ == "__main__":
    main()
