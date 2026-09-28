from pathlib import Path

from app.connectors.mock import MockApplicationConnector, MockJobConnector


def test_mock_job_connector():
    c = MockJobConnector()
    jobs = c.discover_jobs()
    assert len(jobs) == 4 and c.discover_jobs("analyst")
    assert c.get_job_details(jobs[0].external_id).company == "Example Corp"


def test_discover_endpoint_is_idempotent(client):
    first = client.post("/api/jobs/discover", json={}).json()
    second = client.post("/api/jobs/discover", json={}).json()
    assert first["discovered"] == 4 and second["discovered"] == 0
    assert len(client.get("/api/jobs").json()) == 4


def test_mock_application_connector_requires_confirmation(tmp_path):
    c = MockApplicationConnector()
    c.open("mock://apply/x")
    assert c.detect_blocker() is None
    assert c.submit() is None  # empty form -> not confirmed
    c.open("mock://apply/x-captcha")
    assert "CAPTCHA" in c.detect_blocker()
