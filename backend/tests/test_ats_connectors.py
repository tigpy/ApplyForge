"""Tests for Phase 5: Real ATS form support (Greenhouse, Lever),
safe-run limits (MAX_APPLICATIONS_PER_RUN), rate-limiting, and URL sanity checks.
"""
import http.server
import threading
import time

import pytest
from app.config import settings
from app.connectors.greenhouse import GreenhouseApplicationConnector
from app.connectors.lever import LeverApplicationConnector
from app.connectors.playwright_connector import PlaywrightApplicationConnector
from app.connectors.public_feed import PublicFeedJobConnector
from app.models import Application, ApplicationStatus, Job
from app.services.application_service import apply_application
from app.services.automation_service import AutomationService
from tests.conftest import CYBER_TEXT, upload


class ATSMockServer(http.server.BaseHTTPRequestHandler):
    """Serves Greenhouse and Lever ATS HTML snapshots and a non-application listing page."""

    def do_GET(self):
        path = self.path.split("?")[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if path == "/greenhouse-job":
            html = """<!DOCTYPE html>
<html>
<head><title>Greenhouse Job Application</title></head>
<body>
  <h1>Apply for Senior Security Engineer</h1>
  <form id="application_form" action="/submit-greenhouse" method="post" enctype="multipart/form-data">
    <div class="field">
      <label for="first_name">First Name <span class="asterisk">*</span></label>
      <input type="text" id="first_name" name="first_name" required autocomplete="given-name" />
    </div>
    <div class="field">
      <label for="last_name">Last Name <span class="asterisk">*</span></label>
      <input type="text" id="last_name" name="last_name" required autocomplete="family-name" />
    </div>
    <div class="field">
      <label for="email">Email <span class="asterisk">*</span></label>
      <input type="email" id="email" name="email" required autocomplete="email" />
    </div>
    <div class="field">
      <label for="phone">Phone</label>
      <input type="tel" id="phone" name="phone" autocomplete="tel" />
    </div>
    <div class="field">
      <label for="resume">Resume/CV <span class="asterisk">*</span></label>
      <input type="file" id="resume" name="resume" required />
    </div>
    <div class="field">
      <label for="job_application_answers_attributes_0_text_value">LinkedIn Profile</label>
      <input type="text" id="job_application_answers_attributes_0_text_value" name="job_application[answers_attributes][0][text_value]" placeholder="linkedin.com/in/..." />
    </div>
    <div class="field">
      <label for="auth_select">Are you legally authorized to work in the country?</label>
      <select id="auth_select" name="job_application[answers_attributes][1][text_value]">
        <option value="">-- Please select --</option>
        <option value="Yes">Yes</option>
        <option value="No">No</option>
      </select>
    </div>
    <div id="submit_app_container">
      <input type="submit" id="submit_app" value="Submit Application" />
    </div>
  </form>
</body>
</html>"""

        elif path == "/lever-job":
            html = """<!DOCTYPE html>
<html>
<head><title>Lever Job Posting</title></head>
<body>
  <div class="application-page">
    <h1>Software Security Engineer</h1>
    <form id="application-form" class="application-form" action="/submit-lever" method="post" enctype="multipart/form-data">
      <ul class="application-fields">
        <li>
          <label>Full name <span class="required">*</span></label>
          <input type="text" name="name" required />
        </li>
        <li>
          <label>Email <span class="required">*</span></label>
          <input type="email" name="email" required />
        </li>
        <li>
          <label>Phone </label>
          <input type="tel" name="phone" />
        </li>
        <li>
          <label>Current company </label>
          <input type="text" name="org" />
        </li>
        <li>
          <label>LinkedIn URL </label>
          <input type="url" name="urls[LinkedIn]" />
        </li>
        <li>
          <label>GitHub URL </label>
          <input type="url" name="urls[GitHub]" />
        </li>
        <li class="application-field">
          <label>Resume/CV <span class="required">*</span></label>
          <input type="file" id="resume-upload-input" name="resume" required />
        </li>
        <li>
          <label>Additional information </label>
          <textarea name="comments" placeholder="Add a cover letter or anything else you'd like to share"></textarea>
        </li>
      </ul>
      <div class="action-wrapper">
        <button id="btn-submit" type="submit" class="template-btn-submit">Submit Application</button>
      </div>
    </form>
  </div>
</body>
</html>"""

        elif path == "/job-listing-only":
            html = """<!DOCTYPE html>
<html>
<head><title>Company Careers - Job Listing</title></head>
<body>
  <h1>Security Analyst Position</h1>
  <p>We are looking for a security analyst. Please apply on our partner portal.</p>
  <a href="https://external-careers.example.com/apply">Apply on Partner Site</a>
  <form action="/newsletter" method="post">
    <label for="newsletter">Sign up for job alerts:</label>
    <input type="email" id="newsletter" name="newsletter_email" placeholder="Your email" />
    <button type="submit">Subscribe</button>
  </form>
</body>
</html>"""

        else:
            html = "<html><body><h1>Not Found</h1></body></html>"

        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(content_length)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        path = self.path.split("?")[0]
        if path == "/submit-greenhouse":
            confirm = """<!DOCTYPE html>
<html><head><title>Thank you</title></head>
<body>
  <div id="confirmation_page">
    <h1>Thank you for applying!</h1>
    <p>Your application was submitted successfully.</p>
  </div>
</body></html>"""
        elif path == "/submit-lever":
            confirm = """<!DOCTYPE html>
<html><head><title>Application Submitted</title></head>
<body>
  <h1>Thank you for applying</h1>
  <p>We have received your application. Our team will review your profile shortly.</p>
</body></html>"""
        else:
            confirm = "<html><body><h1>Success</h1></body></html>"

        self.wfile.write(confirm.encode("utf-8"))

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def ats_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), ATSMockServer)
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


def test_greenhouse_connector_filling_and_confirmation(client, db, ats_server):
    """Verifies Greenhouse ATS form detection, field mapping, file upload, and submission confirmation."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
        "phone": "+1 555 9876",
        "linkedin": "https://linkedin.com/in/aryansharma",
        "facts": {"work_authorization": "Yes"},
    })

    job = Job(
        company="Stripe",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="gh-stripe-1",
        fingerprint="stripe|sec|remote",
        description="Security analysis position.",
        requirements=["Python", "Linux", "SIEM"],
        application_url=f"{ats_server}/greenhouse-job",
    )
    db.add(job)
    db.commit()

    client.post(f"/api/jobs/{job.id}/match")
    app_id = client.get(f"/api/jobs/{job.id}").json()["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.APPLIED.value
    assert result.submitted_at is not None
    assert "greenhouse confirmation" in result.confirmation_text.lower()
    assert result.resume.filename == "cybersecurity.pdf"


def test_lever_connector_filling_and_confirmation(client, db, ats_server):
    """Verifies Lever ATS form detection, field mapping, file upload, and submission confirmation."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
        "phone": "+1 555 9876",
        "linkedin": "https://linkedin.com/in/aryansharma",
        "github": "https://github.com/aryansharma",
    })

    job = Job(
        company="GitLab",
        title="Security Engineer",
        location="Remote",
        source="mock",
        external_id="lever-gitlab-1",
        fingerprint="gitlab|sec|remote",
        description="Security engineer position.",
        requirements=["Python", "Linux", "SIEM"],
        application_url=f"{ats_server}/lever-job",
    )
    db.add(job)
    db.commit()

    client.post(f"/api/jobs/{job.id}/match")
    app_id = client.get(f"/api/jobs/{job.id}").json()["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.APPLIED.value
    assert result.submitted_at is not None
    assert "lever confirmation" in result.confirmation_text.lower()
    assert result.resume.filename == "cybersecurity.pdf"


def test_unsupported_platform_job_listing_marked_blocked(client, db, ats_server):
    """Verifies sanity check: pages that are merely job listings without real application forms are marked BLOCKED."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={"name": "Aryan Sharma", "email": "aryan@example.com"})

    job = Job(
        company="External Portal Corp",
        title="Security Analyst",
        location="Remote",
        source="mock",
        external_id="listing-only-1",
        fingerprint="epc|sec|remote",
        description="Position without direct form.",
        requirements=["Python", "Linux", "SIEM"],
        application_url=f"{ats_server}/job-listing-only",
    )
    db.add(job)
    db.commit()

    client.post(f"/api/jobs/{job.id}/match")
    app_id = client.get(f"/api/jobs/{job.id}").json()["application_id"]

    conn = PlaywrightApplicationConnector(headless=True)
    result = apply_application(db, app_id, connector=conn)

    assert result.status == ApplicationStatus.BLOCKED.value
    assert "unsupported application platform" in result.failure_reason.lower()


def test_max_applications_per_run_cap(client, db):
    """Verifies that AutomationService halts auto-applying once MAX_APPLICATIONS_PER_RUN is reached."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    client.put("/api/profile", json={
        "name": "Aryan Sharma",
        "email": "aryan@example.com",
        "facts": {"work_authorization": "Yes"},
    })

    # Create 4 jobs that match cybersecurity.pdf with 90%+ score
    for i in range(1, 5):
        j = Job(
            company=f"Batch Corp {i}",
            title=f"Security Analyst {i}",
            location="Remote",
            source="mock",
            external_id=f"batch-cap-{i}",
            fingerprint=f"batch|sec|{i}",
            description="Security analyst role.",
            requirements=["Python", "Linux", "SIEM"],
            application_url=f"mock://apply/batch-{i}",
        )
        db.add(j)
    db.commit()

    orig_cap = settings.max_applications_per_run
    settings.max_applications_per_run = 2

    try:
        service = AutomationService(db)
        result = service.run_job_search(connector_name="mock", query="Batch Corp", auto_apply=True)

        assert result.applied == 2
        assert result.remaining >= 1
    finally:
        settings.max_applications_per_run = orig_cap


def test_public_feed_rate_limiting():
    """Verifies that PublicFeedJobConnector caches online results to avoid hammering outbound servers."""
    conn = PublicFeedJobConnector()
    jobs1 = conn.discover_jobs()
    t2 = time.time()
    jobs2 = conn.discover_jobs()
    cached_duration = time.time() - t2
    # Second call should complete virtually instantaneously via memory cache
    assert len(jobs1) == len(jobs2)
    assert cached_duration < 0.2
