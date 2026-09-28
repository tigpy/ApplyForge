"""Generate two small sample resume PDFs for local testing / the E2E fixture.

Usage (with backend venv active):  python scripts/make_sample_resumes.py [output_dir]
Default output: data/sample-resumes
"""
import sys
from pathlib import Path

import pymupdf

SAMPLES = {
    "cybersecurity.pdf": (
        "Sample Candidate - Cybersecurity resume.\nSkills: Python, Linux, SIEM, Splunk, incident response, "
        "networking, TCP/IP, Wireshark, log analysis, vulnerability assessment.\nMonitored security alerts in a SOC lab."
    ),
    "backend.pdf": (
        "Sample Candidate - Backend resume.\nSkills: Python, FastAPI, SQL, REST APIs, Git, Docker.\nBuilt API services."
    ),
}


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "sample-resumes"
    out.mkdir(parents=True, exist_ok=True)
    for name, text in SAMPLES.items():
        doc = pymupdf.open()
        doc.new_page().insert_textbox(pymupdf.Rect(50, 50, 550, 780), text, fontsize=11)
        doc.save(out / name)
        doc.close()
        print("wrote", out / name)


if __name__ == "__main__":
    main()
