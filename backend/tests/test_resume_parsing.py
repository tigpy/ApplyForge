from app.security import sanitize_filename
from app.services.resume_service import PyMuPDFResumeParser
from tests.conftest import CYBER_TEXT, make_pdf, upload


def test_parser_extracts_text(tmp_path):
    f = tmp_path / "r.pdf"
    f.write_bytes(make_pdf(CYBER_TEXT))
    assert "SIEM" in PyMuPDFResumeParser().extract_text(f)


def test_upload_list_delete(client):
    r = upload(client, "cybersecurity.pdf", CYBER_TEXT)
    assert r.status_code == 201 and r.json()["extracted_chars"] > 20
    assert len(client.get("/api/resumes").json()) == 1
    assert client.delete(f"/api/resumes/{r.json()['id']}").status_code == 204
    assert client.get("/api/resumes").json() == []


def test_upload_rejects_non_pdf(client):
    r = client.post("/api/resumes/upload", files={"file": ("evil.exe", b"MZ...", "application/octet-stream")})
    assert r.status_code == 415
    r = client.post("/api/resumes/upload", files={"file": ("fake.pdf", b"not a pdf", "application/pdf")})
    assert r.status_code == 415


def test_filename_sanitized():
    assert sanitize_filename("../../etc/pass wd.pdf") == "pass_wd.pdf"
    assert sanitize_filename("..\\..\\x.pdf") == "x.pdf"
