"""Phase 4B Automated Application Layer Tests.
Tests all 12 core scenarios:
1. One job + one resume test
2. One job + multiple resumes test
3. Best resume selection test
4. Match score calculation test
5. Missing skills test
6. Application creation test
7. Successful mock application test
8. Failed / blocked application test
9. Duplicate application prevention test
10. Application result persistence and endpoint test
11. Notification event test
12. Complete automation workflow test
"""
from app.models import Application, ApplicationStatus as S, Job
from app.services.automation_service import run_automation, run_job_application
from app.services.job_service import make_fingerprint
from app.services.notification_service import MockNotificationService
from tests.conftest import BACKEND_TEXT, CYBER_TEXT, upload


def test_1_one_job_one_resume(client):
    """Scenario 1: Evaluates one job against a single uploaded resume."""
    assert upload(client, "backend.pdf", BACKEND_TEXT).status_code == 201
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]
    target_job = next(j for j in jobs if "Backend" in j["title"])

    res = client.post(f"/api/jobs/{target_job['id']}/match")
    assert res.status_code == 200
    data = res.json()
    assert data["selected_resume_name"] == "backend.pdf"
    assert data["score"] > 50
    matched_lower = [s.lower() for s in data["matched_skills"]]
    assert "fastapi" in matched_lower or "python" in matched_lower
    assert len(data["resume_scores"]) == 1


def test_2_one_job_multiple_resumes(client):
    """Scenario 2: Evaluates one job against all uploaded resumes."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    upload(client, "backend.pdf", BACKEND_TEXT)
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]
    target_job = next(j for j in jobs if "Junior Security Analyst" in j["title"])

    res = client.post(f"/api/jobs/{target_job['id']}/match")
    assert res.status_code == 200
    data = res.json()
    assert len(data["resume_scores"]) == 2
    scored_names = {s["resume_name"] for s in data["resume_scores"]}
    assert "cybersecurity.pdf" in scored_names
    assert "backend.pdf" in scored_names


def test_3_best_resume_selection(client):
    """Scenario 3: Automatically selects the highest-scoring resume for each role."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    upload(client, "backend.pdf", BACKEND_TEXT)
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]

    sec_job = next(j for j in jobs if "Junior Security Analyst" in j["title"])
    backend_job = next(j for j in jobs if "Backend Python Developer" in j["title"])

    m_sec = client.post(f"/api/jobs/{sec_job['id']}/match").json()
    m_backend = client.post(f"/api/jobs/{backend_job['id']}/match").json()

    assert m_sec["selected_resume_name"] == "cybersecurity.pdf"
    assert m_backend["selected_resume_name"] == "backend.pdf"
    assert m_sec["score"] >= 75
    assert m_backend["score"] >= 75


def test_4_match_score_calculation(client):
    """Scenario 4: Match score calculation is deterministic (0-100) and includes breakdown."""
    upload(client, "cybersecurity.pdf", CYBER_TEXT)
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]
    job = jobs[0]

    data = client.post(f"/api/jobs/{job['id']}/match").json()
    assert 0 <= data["score"] <= 100
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "explanation" in data
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["missing_skills"], list)


def test_5_missing_skills(client, db):
    """Scenario 5: Correctly identifies missing skills and reflects gaps in score."""
    upload(client, "backend.pdf", BACKEND_TEXT)
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]
    job_id = jobs[0]["id"]

    # Inject requirements that backend resume does NOT have
    job = db.get(Job, job_id)
    job.requirements = ["Rust", "Kubernetes", "Splunk", "Solidity"]
    db.commit()

    data = client.post(f"/api/jobs/{job_id}/match").json()
    assert data["recommendation"] == "SKIP"
    assert "kubernetes" in [s.lower() for s in data["missing_skills"]]
    assert "rust" in [s.lower() for s in data["missing_skills"]]
    assert data["score"] < 50


def test_6_application_creation(client, seeded):
    """Scenario 6: Matching creates or updates the Application record with selected resume."""
    job = seeded["Junior Security Analyst"]
    match_data = client.post(f"/api/jobs/{job['id']}/match").json()

    app_id = match_data["application_id"]
    assert app_id is not None

    res = client.get(f"/api/applications/{app_id}")
    assert res.status_code == 200
    app_data = res.json()
    assert app_data["job_id"] == job["id"]
    assert app_data["resume_name"] == "cybersecurity.pdf"
    assert app_data["status"] == "ELIGIBLE"


def test_7_successful_mock_application(client, seeded):
    """Scenario 7: Full application flow through mock connector results in APPLIED state."""
    job = seeded["Junior Security Analyst"]
    res = client.post(f"/api/jobs/{job['id']}/apply")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "APPLIED"
    assert data["resume_name"] == "cybersecurity.pdf"
    assert data["submitted_at"] is not None
    assert "application received" in data["confirmation_text"].lower()
    assert len(MockNotificationService.sent) == 1


def test_8_failed_or_blocked_application(client, seeded):
    """Scenario 8: Application that hits a block (e.g. CAPTCHA) transitions to BLOCKED safely."""
    job = seeded["Security Engineer"]  # mock connector triggers CAPTCHA on this job
    res = client.post(f"/api/jobs/{job['id']}/apply")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "BLOCKED"
    assert "CAPTCHA" in data["failure_reason"]
    # Notification sent regarding the failure/block
    assert len(MockNotificationService.sent) == 1
    assert "CAPTCHA" in MockNotificationService.sent[0].body


def test_9_duplicate_application_prevention(client, seeded, db):
    """Scenario 9: Re-applying to an already applied job returns without duplicate submission."""
    job = seeded["Junior Security Analyst"]

    # First apply
    r1 = client.post(f"/api/jobs/{job['id']}/apply")
    assert r1.status_code == 200
    assert r1.json()["status"] == "APPLIED"
    assert len(MockNotificationService.sent) == 1

    # Second apply to same job
    r2 = client.post(f"/api/jobs/{job['id']}/apply")
    assert r2.status_code == 200
    assert r2.json()["status"] == "APPLIED"
    # No second notification was sent
    assert len(MockNotificationService.sent) == 1

    # Twin job duplicate prevention
    orig = db.get(Job, job["id"])
    twin = Job(
        company=orig.company,
        title=orig.title,
        location=orig.location,
        source="other",
        external_id="twin-test-9",
        fingerprint=make_fingerprint(orig.company, orig.title, orig.location),
        requirements=orig.requirements,
        application_url="mock://apply/example-twin",
    )
    db.add(twin)
    db.commit()

    twin_res = run_job_application(db, twin.id)
    assert twin_res.status == S.DUPLICATE.value
    assert len(MockNotificationService.sent) == 1


def test_10_application_result_persistence(client, seeded):
    """Scenario 10: GET /api/applications/{id}/result returns persisted result with all fields."""
    job = seeded["Junior Security Analyst"]
    apply_res = client.post(f"/api/jobs/{job['id']}/apply").json()
    app_id = apply_res["id"]

    result_res = client.get(f"/api/applications/{app_id}/result")
    assert result_res.status_code == 200
    result = result_res.json()

    assert result["application_id"] == app_id
    assert result["job_id"] == job["id"]
    assert result["company"] == "Example Corp"
    assert result["role"] == "Junior Security Analyst"
    assert result["selected_resume_id"] is not None
    assert result["resume_name"] == "cybersecurity.pdf"
    assert result["match_score"] >= 75
    assert result["status"] == "APPLIED"
    assert result["submitted_at"] is not None
    assert result["confirmation_text"] is not None


def test_11_notification_event(client, seeded):
    """Scenario 11: Notification dispatched after successful application contains required metadata."""
    job = seeded["Junior Security Analyst"]
    client.post(f"/api/jobs/{job['id']}/apply")

    assert len(MockNotificationService.sent) == 1
    notification = MockNotificationService.sent[0]
    body = notification.body

    assert "Company: Example Corp" in body
    assert "Junior Security Analyst" in body or "Role:" in body
    assert "Resume used: cybersecurity.pdf" in body
    assert "Status: Applied" in body


def test_12_complete_automation_workflow(client, seeded, db):
    """Scenario 12: run_automation executes end-to-end multi-job discovery, matching, and applying."""
    result = run_automation(db, connector_name="mock", query="", min_match_score=75)

    assert result.discovered >= 0
    assert result.matched >= 1
    assert result.applied >= 1
    assert len(result.details) >= 1

    detail = result.details[0]
    assert "job_id" in detail
    assert "company" in detail
    assert "role" in detail
    assert "resume" in detail
    assert "match_score" in detail
    assert "status" in detail
    assert "message" in detail
