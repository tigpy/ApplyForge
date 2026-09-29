"""Tests for Phase 5A: Real Browser Application Automation (Playwright).
Tests all required local mock HTML page scenarios:
A. Normal application form filling and submission
B. Resume upload ensuring Phase 4B selected resume is used
C. Unknown mandatory question -> REQUIRES_MANUAL_ACTION
D. CAPTCHA page -> BLOCKED
E. Cloudflare challenge -> BLOCKED
F. Already-applied page -> DUPLICATE
G. Successful confirmation verification
H. Dry-run mode verification (inspects, plans, does not submit)
I. Login required page -> BLOCKED
"""
import http.server
import threading
from urllib.parse import parse_qs

import pytest
from app.config import settings
from app.connectors.playwright_connector import PlaywrightApplicationConnector
from app.models import ApplicationStatus, Job
from app.services.application_service import apply_application
from app.services.matching_service import run_match
from tests.conftest import CYBER_TEXT, make_pdf, upload


class MockPortalServer(http.server.BaseHTTPRequestHandler):
    """Local HTTP server serving various application page scenarios."""

    def do_GET(self):
        path = self.path.split("?")[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if path == "/normal-form":
            html = """<!DOCTYPE html>
<html>
<head><title>Engineering Jobs</title></head>
<body>
  <h1>Apply for Senior Analyst</h1>
  <form action="/submit-normal" method="post" enctype="multipart/form-data">
    <label for="first_name">First Name</label>
    <input id="first_name" name="first_name" type="text" required /><br/>

    <label for="last_name">Last Name</label>
    <input id="last_name" name="last_name" type="text" required /><br/>

    <label for="email">Email</label>
    <input id="email" name="email" type="email" required /><br/>

    <label for="phone">Phone</label>
    <input id="phone" name="phone" type="tel" /><br/>

    <label for="city">City</label>
    <input id="city" name="city" type="text" /><br/>

    <label for="linkedin">LinkedIn Profile</label>
    <input id="linkedin" name="linkedin" type="url" /><br/>

    <label for="work_auth">Are you authorized to work in this country?</label>
    <select id="work_auth" name="work_auth" required>
      <option value="">-- Please select --</option>
      <option value="Yes">Yes, I am authorized</option>
      <option value="No">No</option>
    </select><br/>

    <label for="resume">Upload Resume</label>
    <input id="resume" name="resume" type="file" required /><br/>

    <button type="submit" id="submit-btn">Submit Application</button>
  </form>
</body>
</html>"""

        elif path == "/resume-upload-form":
            html = """<!DOCTYPE html>
<html>
<head><title>Submit CV</title></head>
<body>
  <h1>Resume Submission</h1>
  <form action="/submit-resume" method="post" enctype="multipart/form-data">
    <label for="name">Full Name</label>
    <input id="name" name="name" type="text" required /><br/>

    <label for="email">Email Address</label>
    <input id="email" name="email" type="email" required /><br/>

    <label for="cv">Resume Document (PDF)</label>
    <input id="cv" name="cv" type="file" required /><br/>

    <input type="submit" value="Apply Now" />
  </form>
</body>
</html>"""

        elif path == "/unknown-mandatory":
            html = """<!DOCTYPE html>
<html>
<head><title>Special Access Role</title></head>
<body>
  <h1>Government Security Role</h1>
  <form action="/submit-normal" method="post">
    <label for="name">Full Name</label>
    <input id="name" name="name" type="text" required /><br/>

    <label for="clearance_code">Top Secret Security Clearance Badge Number</label>
    <input id="clearance_code" name="clearance_code" type="text" required /><br/>

    <button type="submit">Submit</button>
  </form>
</body>
</html>"""

        elif path == "/captcha-page":
            html = """<!DOCTYPE html>
<html>
<head><title>Security Check</title></head>
<body>
  <h1>Please verify you are human</h1>
  <div class="g-recaptcha" data-sitekey="sample"></div>
  <p>Complete the captcha verification to view the application.</p>
</body>
</html>"""

        elif path == "/cloudflare-page":
            html = """<!DOCTYPE html>
<html>
<head><title>Just a moment...</title></head>
<body>
  <h1>Checking your browser</h1>
  <div class="cf-turnstile"></div>
  <p>Attention Required! | Cloudflare bot protection is verifying your connection.</p>
</body>
</html>"""

        elif path == "/already-applied":
            html = """<!DOCTYPE html>
<html>
<head><title>Candidate Status</title></head>
<body>
  <h1>Application Status</h1>
  <p>You have already applied for this position. We have your application on file.</p>
</body>
</html>"""

        elif path == "/login-required":
            html = """<!DOCTYPE html>
<html>
<head><title>Sign In Required</title></head>
<body>
  <h1>Please sign in to apply</h1>
  <p>You must be signed in to apply for this job opening.</p>
</body>
</html>"""

        else:
            html = "<html><body><h1>Not Found</h1></body></html>"

        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        confirm_html = """<!DOCTYPE html>
<html>
<head><title>Confirmation</title></head>
<body>
  <h1>Application Received</h1>
  <p>Thank you for applying! Your application has been successfully submitted.</p>
</body>
</html>"""
        self.wfile.write(confirm_html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # quiet test logs


@pytest.fixture(scope="module")
def portal_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), MockPortalServer)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    orig_allow = settings.allow_local_urls
    settings.allow_local_urls = True

    yield base_url

    settings.allow_local_urls = orig_allow
    server.shutdown()
    server.server_close()


def test_browser_normal_application_form(client, db, portal_server):
    """Scenario A: Form filling and confirmation extraction on a standard form."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
        "phone": "+1 555 1234",
        "location": "Mumbai, India",
        "linkedin": "https://linkedin.com/in/aryansharma",
        "facts": {"work_authorization": "Yes"},
    })

    job = Job(
        company="Global Tech Corp",
        title="Security Analyst",
        location="Mumbai",
        source="mock",
        external_id="browser-test-normal",
        fingerprint="gtc|sec|mumbai",
        description="Analyst role.",
        requirements=["Python", "Linux", "SIEM"],
        application_url=f"{portal_server}/normal-form",
    )
    db.add(job)
    db.commit()

    # Match and get application
    client.post(f"/api/jobs/{job.id}/match")
    app = client.get(f"/api/jobs/{job.id}").json()["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app, connector=conn)

    print("TEST DEBUG failure_reason:", result.failure_reason)
    assert result.status == ApplicationStatus.APPLIED.value
    assert result.submitted_at is not None
    assert "thank you for applying" in result.confirmation_text.lower()


def test_browser_resume_upload_uses_phase4b_selected_resume(client, db, portal_server):
    """Scenario B: Ensures resume upload uses the resume chosen by Phase 4B matching."""
    # Upload cybersecurity resume and backend resume
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    upload(client, "backend.pdf", "Python, FastAPI, SQL, REST APIs backend developer resume.")

    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
    })

    job = Job(
        company="Security Solutions Ltd",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-resume",
        fingerprint="ssl|sec|remote",
        description="SIEM, Linux, and incident response specialist.",
        requirements=["SIEM", "Incident response", "Linux"],
        application_url=f"{portal_server}/resume-upload-form",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    assert match_res["selected_resume_name"] == "cybersecurity.pdf"
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.APPLIED.value
    assert result.resume.filename == "cybersecurity.pdf"


def test_browser_unknown_mandatory_question_requires_manual_action(client, db, portal_server):
    """Scenario C: Unknown mandatory question returns REQUIRES_MANUAL_ACTION."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
    })

    job = Job(
        company="GovSec Defense",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-unknown",
        fingerprint="govsec|sec|remote",
        description="Security clearance role.",
        requirements=["Python", "Linux"],
        application_url=f"{portal_server}/unknown-mandatory",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.REQUIRES_MANUAL_ACTION.value
    assert "manual input needed" in result.failure_reason.lower()


def test_browser_captcha_detected_halts_with_blocked(client, db, portal_server):
    """Scenario D: CAPTCHA detection immediately stops and returns BLOCKED."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={"name": "Aryan Sharma", "email": "aryan@example.com"})

    job = Job(
        company="Shield Wall Corp",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-captcha",
        fingerprint="swc|sec|remote",
        description="Security role.",
        requirements=["Python"],
        application_url=f"{portal_server}/captcha-page",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.BLOCKED.value
    assert "captcha" in result.failure_reason.lower()


def test_browser_cloudflare_challenge_halts_with_blocked(client, db, portal_server):
    """Scenario E: Cloudflare bot challenge stops and returns BLOCKED."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={"name": "Aryan Sharma", "email": "aryan@example.com"})

    job = Job(
        company="Cloud Fortress Inc",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-cloudflare",
        fingerprint="cfi|sec|remote",
        description="Security role.",
        requirements=["Python"],
        application_url=f"{portal_server}/cloudflare-page",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.BLOCKED.value
    assert "cloudflare" in result.failure_reason.lower()


def test_browser_already_applied_returns_duplicate(client, db, portal_server):
    """Scenario F: Page indicates application is already submitted -> DUPLICATE."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={"name": "Aryan Sharma", "email": "aryan@example.com"})

    job = Job(
        company="Existing Candidate Corp",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-already-applied",
        fingerprint="ecc|sec|remote",
        description="Security role.",
        requirements=["Python"],
        application_url=f"{portal_server}/already-applied",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.DUPLICATE.value
    assert "already applied" in result.failure_reason.lower()


def test_browser_login_required_returns_blocked(client, db, portal_server):
    """Scenario I: Page requiring sign in / login halts with BLOCKED."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={"name": "Aryan Sharma", "email": "aryan@example.com"})

    job = Job(
        company="Auth Portal Corp",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="browser-test-login",
        fingerprint="auth|sec|remote",
        description="Security role.",
        requirements=["Python"],
        application_url=f"{portal_server}/login-required",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.BLOCKED.value
    assert "login" in result.failure_reason.lower()


def test_browser_dry_run_inspects_and_does_not_submit(client, db, portal_server):
    """Scenario H: Dry-run inspects form, plans fields, verifies resume, stops before submit."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
        "phone": "+1 555 1234",
        "location": "Mumbai, India",
        "facts": {"work_authorization": "Yes"},
    })

    job = Job(
        company="Dry Run Tech",
        title="Security Analyst",
        location="Mumbai",
        source="mock",
        external_id="browser-test-dryrun",
        fingerprint="drt|sec|mumbai",
        description="Analyst position for dry run.",
        requirements=["Python"],
        application_url=f"{portal_server}/normal-form",
    )
    db.add(job)
    db.commit()

    match_res = client.post(f"/api/jobs/{job.id}/match").json()
    app_id = match_res["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn, dry_run=True)

    # Status remains ELIGIBLE (not APPLIED)
    assert result.status == ApplicationStatus.ELIGIBLE.value
    assert result.submitted_at is None
    assert "dry run passed" in result.confirmation_text.lower()
    assert "simulated" in result.confirmation_text.lower()
