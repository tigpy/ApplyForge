"""Integration tests for ApplyForge full workflow, multi-resume matching, automation run, and real Playwright browser automation."""
import http.server
import threading
from pathlib import Path

import pytest
from app.config import settings
from app.connectors.playwright_connector import PlaywrightApplicationConnector
from app.models import ApplicationStatus, Job
from app.services.application_service import apply_application
from app.services.matching_service import run_match
from app.services.notification_service import MockNotificationService
from tests.conftest import make_pdf, upload

# ----------------- Sample resume texts -----------------
CYBER_TEXT = (
    "Aryan Sharma - Cybersecurity Analyst. Location: Mumbai. "
    "Skills: Python, Linux, SIEM, Splunk, Incident response, Networking, TCP/IP, Wireshark, Log analysis, Vulnerability assessment."
)
SOC_TEXT = (
    "Aryan Sharma - SOC Analyst. Location: Mumbai. "
    "Skills: SIEM, Splunk, Log analysis, Incident response, Linux, Networking, Wireshark, MITRE ATT&CK."
)
BACKEND_TEXT = (
    "Aryan Sharma - Backend Developer. Location: Mumbai. "
    "Skills: Python, FastAPI, SQL, PostgreSQL, REST API, Git, Docker, Linux."
)
JAVA_TEXT = (
    "Aryan Sharma - Java Developer. Location: Mumbai. "
    "Skills: Java, Spring Boot, SQL, MySQL, REST API, Git, Linux, Docker."
)
FRESHER_TEXT = (
    "Aryan Sharma - Junior Developer. Location: Mumbai. "
    "Skills: Python, JavaScript, Git, Linux, SQL, HTML, CSS."
)


def test_resume_upload_extraction_and_duplicate_prevention(client):
    """1. Upload resume, 2. Extract resume, 3. Duplicate prevention."""
    r1 = upload(client, "cybersecurity.pdf", CYBER_TEXT)
    assert r1.status_code == 201
    body = r1.json()
    assert body["filename"] == "cybersecurity.pdf"
    assert "extracted_text" in body and "SIEM" in body["extracted_text"]

    # Duplicate upload of identical file should be rejected with 409
    r_dup = upload(client, "cybersecurity.pdf", CYBER_TEXT)
    assert r_dup.status_code == 409
    assert "already exists" in r_dup.json()["detail"]


def test_multi_resume_matching_selects_best_resume(client, db):
    """Matches different jobs against multiple resumes and ensures the best resume is selected."""
    assert upload(client, "cybersecurity.pdf", CYBER_TEXT).status_code == 201
    assert upload(client, "soc-analyst.pdf", SOC_TEXT).status_code == 201
    assert upload(client, "backend.pdf", BACKEND_TEXT).status_code == 201
    assert upload(client, "java.pdf", JAVA_TEXT).status_code == 201

    # 1. SOC Analyst Job
    soc_job = Job(
        company="CyberGuard", title="SOC Analyst", location="Mumbai",
        source="mock", external_id="cg-soc-1", fingerprint="cg|soc|mumbai",
        description="Tier 1 SOC Analyst responsible for SIEM alerts and incident response.",
        requirements=["SIEM", "Splunk", "Incident response", "Log analysis", "Linux"],
    )
    db.add(soc_job)
    db.commit()

    m_soc = run_match(db, soc_job)
    # The selected resume should be either soc-analyst.pdf or cybersecurity.pdf, NOT backend or java
    resume_soc = client.get(f"/api/jobs/{soc_job.id}").json()["match"]
    assert resume_soc["selected_resume_name"] in ("soc-analyst.pdf", "cybersecurity.pdf")
    assert resume_soc["score"] >= 80

    # 2. Python Backend Job
    py_job = Job(
        company="PyCloud", title="Backend Python Engineer", location="Remote",
        source="mock", external_id="py-1", fingerprint="py|backend|remote",
        description="Build scalable REST APIs with Python, FastAPI and SQL.",
        requirements=["Python", "FastAPI", "SQL", "REST API", "Docker", "Git"],
    )
    db.add(py_job)
    db.commit()

    m_py = run_match(db, py_job)
    resume_py = client.get(f"/api/jobs/{py_job.id}").json()["match"]
    assert resume_py["selected_resume_name"] == "backend.pdf"
    assert resume_py["score"] >= 80

    # 3. Java Developer Job
    java_job = Job(
        company="Enterprise Java Corp", title="Java Software Engineer", location="Mumbai",
        source="mock", external_id="java-1", fingerprint="corp|java|mumbai",
        description="Build enterprise services using Java and Spring Boot.",
        requirements=["Java", "Spring Boot", "SQL", "MySQL", "Git"],
    )
    db.add(java_job)
    db.commit()

    m_java = run_match(db, java_job)
    resume_java = client.get(f"/api/jobs/{java_job.id}").json()["match"]
    assert resume_java["selected_resume_name"] == "java.pdf"
    assert resume_java["score"] >= 80


def test_full_automation_run_job_search(client):
    """Tests the full Run Job Search action: discover -> match -> rank -> auto-apply -> record -> notify."""
    # 1. Upload resumes
    assert upload(client, "cybersecurity.pdf", CYBER_TEXT).status_code == 201
    assert upload(client, "backend.pdf", BACKEND_TEXT).status_code == 201

    # 2. Save preferences and profile
    pref_res = client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan.sharma@example.com",
        "phone": "+91 9876543210",
        "location": "Mumbai, India",
        "target_roles": ["Junior Security Analyst", "SOC Analyst", "Backend Python Developer"],
        "preferred_locations": ["Mumbai", "Remote"],
        "remote_preference": "all",
        "preferred_job_sources": ["mock"],
        "facts": {"work_authorization": "Yes"},
    })
    assert pref_res.status_code == 200

    # 3. Execute "Run Job Search"
    run_res = client.post("/api/automation/run", json={"auto_apply": True})
    assert run_res.status_code == 200
    data = run_res.json()

    assert data["discovered"] >= 4
    assert data["matched"] >= 4
    assert data["eligible"] >= 1
    # At least Example Corp (Junior Security Analyst) and Northwind (with work auth fact) apply successfully
    assert data["applied"] >= 1
    assert len(MockNotificationService.sent) >= 1

    # Verify notifications contain structured records
    applied_notifications = [n for n in MockNotificationService.sent if "Applied Successfully" in n.body]
    assert len(applied_notifications) >= 1
    first_note = applied_notifications[0].body
    assert "Company:" in first_note
    assert "Resume used:" in first_note
    assert "Match:" in first_note
    assert "Status: Applied" in first_note

    # 4. Check application history
    apps = client.get("/api/applications").json()
    assert len(apps) >= 1
    statuses = [a["status"] for a in apps]
    assert "APPLIED" in statuses


# ----------------- Local HTTP Server for Playwright Automation -----------------
class _LocalMockJobAppHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        html = """<!DOCTYPE html>
<html>
<head><title>Job Application Portal</title></head>
<body>
  <h1>Apply for Security Analyst</h1>
  <form action="/submit" method="post" enctype="multipart/form-data">
    <label for="full_name">Full name</label>
    <input id="full_name" name="full_name" type="text" required /><br/>

    <label for="email">Email address</label>
    <input id="email" name="email" type="email" required /><br/>

    <label for="phone">Phone number</label>
    <input id="phone" name="phone" type="tel" /><br/>

    <label for="resume">Resume (PDF)</label>
    <input id="resume" name="resume" type="file" required /><br/>

    <button type="submit" id="submit-btn">Submit Application</button>
  </form>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        # Read payload
        content_length = int(self.headers.get("Content-Length", 0))
        _ = self.rfile.read(content_length)

        confirm_html = """<!DOCTYPE html>
<html>
<head><title>Confirmation</title></head>
<body>
  <h1>Application Received</h1>
  <p>Thank you for applying! We have received your application.</p>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(confirm_html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # quiet test logging


def test_playwright_real_browser_application(client, db):
    """Tests PlaywrightApplicationConnector running headless Chromium against a local mock application page."""
    # Start local mock application web server on an ephemeral port
    server = http.server.HTTPServer(("127.0.0.1", 0), _LocalMockJobAppHandler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    app_url = f"http://127.0.0.1:{port}/"

    # Allow local URL validation for this test
    original_allow = settings.allow_local_urls
    settings.allow_local_urls = True

    try:
        # 1. Upload resume
        upload_resp = upload(client, "cybersecurity.pdf", CYBER_TEXT)
        assert upload_resp.status_code == 201
        resume_id = upload_resp.json()["id"]

        # 2. Set profile candidate information
        client.put("/api/profile", json={
            "name": "Aryan Sharma",
            "email": "aryan.sharma@example.com",
            "phone": "+91 9876543210",
        })

        # 3. Create Job pointing to the local application page
        job = Job(
            company="Local Test Corp",
            title="Junior Security Analyst",
            location="Mumbai, India",
            source="mock",
            external_id="local-playwright-job-1",
            fingerprint="local|security|mumbai",
            description="Security analyst position with local application form.",
            requirements=["Python", "Linux", "SIEM"],
            application_url=app_url,
        )
        db.add(job)
        db.commit()

        # 4. Match job -> ELIGIBLE
        match_out = client.post(f"/api/jobs/{job.id}/match").json()
        assert match_out["application_status"] == "ELIGIBLE"
        app_id = match_out["application_id"]

        # 5. Apply using real Playwright browser connector
        playwright_conn = PlaywrightApplicationConnector(headless=True)
        app_result = apply_application(db, app_id, connector=playwright_conn)

        # 6. Verify result
        assert app_result.status == ApplicationStatus.APPLIED.value
        assert "thank you for applying" in app_result.confirmation_text.lower()
        assert app_result.submitted_at is not None

        # Verify notification
        assert len(MockNotificationService.sent) >= 1
        note = MockNotificationService.sent[-1].body
        assert "Local Test Corp" in note
        assert "cybersecurity.pdf" in note
        assert "Status: Applied" in note

    finally:
        settings.allow_local_urls = original_allow
        server.shutdown()
        server.server_close()
