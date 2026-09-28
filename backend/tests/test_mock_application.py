"""Full backend workflow on mock connectors: resume -> discover -> match -> apply -> APPLIED -> notification."""
from app.services.notification_service import MockNotificationService


def _apply(client, seeded, title):
    job_id = seeded[title]["id"]
    match = client.post(f"/api/jobs/{job_id}/match").json()
    return match, client.post(f"/api/applications/{match['application_id']}/apply")


def test_full_flow_applied_and_notified(client, seeded):
    match, r = _apply(client, seeded, "Junior Security Analyst")
    assert match["application_status"] == "ELIGIBLE"
    body = r.json()
    assert r.status_code == 200 and body["status"] == "APPLIED"
    assert body["resume_name"] == "cybersecurity.pdf" and body["confirmation_text"] and body["submitted_at"]
    events = [e["event"] for e in body["events"]]
    for expected in ("OPENED", "RESUME_SELECTED", "FORM_FILLED", "SUBMITTED", "APPLIED", "NOTIFIED"):
        assert expected in events
    assert len(MockNotificationService.sent) == 1
    sent = MockNotificationService.sent[0].body
    assert "Company: Example Corp" in sent and "Resume used: cybersecurity.pdf" in sent and "Status: Applied" in sent
    assert "test@example.com" not in str(body["events"])  # no PII in event log


def test_cannot_apply_twice(client, seeded):
    match, _ = _apply(client, seeded, "Junior Security Analyst")
    assert client.post(f"/api/applications/{match['application_id']}/apply").status_code == 409
    assert len(MockNotificationService.sent) == 1


def test_captcha_is_blocked_not_bypassed(client, seeded):
    _, r = _apply(client, seeded, "Security Engineer")
    assert r.json()["status"] == "BLOCKED" and "CAPTCHA" in r.json()["failure_reason"]
    assert len(MockNotificationService.sent) == 1
    assert "Application could not be completed" in MockNotificationService.sent[0].body
    assert "CAPTCHA" in MockNotificationService.sent[0].body


def test_unknown_mandatory_question_blocks_then_fact_unblocks(client, seeded):
    match, r = _apply(client, seeded, "SOC Analyst")
    assert r.json()["status"] == "REQUIRES_MANUAL_ACTION" and "authorized" in r.json()["failure_reason"]
    client.put("/api/profile", json={"name": "Test Candidate", "email": "test@example.com",
                                      "facts": {"work_authorization": "Yes"}})
    retry = client.post(f"/api/applications/{match['application_id']}/apply").json()
    assert retry["status"] == "APPLIED"


def test_missing_profile_data_blocks(client, seeded):
    client.put("/api/profile", json={})
    _, r = _apply(client, seeded, "Junior Security Analyst")
    assert r.json()["status"] == "REQUIRES_MANUAL_ACTION" and "Full name" in r.json()["failure_reason"]


def test_duplicate_job_is_not_applied_twice(client, seeded, db):
    from app.models import Job
    from app.services.job_service import make_fingerprint

    _apply(client, seeded, "Junior Security Analyst")
    orig = db.get(Job, seeded["Junior Security Analyst"]["id"])
    twin = Job(company=orig.company, title=orig.title, location=orig.location, source="other", external_id="dup-1",
               fingerprint=make_fingerprint(orig.company, orig.title, orig.location), requirements=orig.requirements,
               application_url="mock://apply/example-corp-jsa")
    db.add(twin)
    db.commit()
    match = client.post(f"/api/jobs/{twin.id}/match").json()
    assert match["application_status"] == "DUPLICATE"


def test_profile_roundtrip_and_test_email(client):
    assert client.get("/api/profile").json()["name"] == ""
    client.put("/api/profile", json={"name": "A", "skills": ["Python"]})
    assert client.get("/api/profile").json()["skills"] == ["Python"]
    assert client.post("/api/settings/test-email").json()["mode"] == "mock"
