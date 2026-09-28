def test_best_resume_selected_per_job(client, seeded):
    resumes = {r["filename"]: r["id"] for r in client.get("/api/resumes").json()}

    m1 = client.post(f"/api/jobs/{seeded['Junior Security Analyst']['id']}/match").json()
    assert m1["selected_resume_id"] == resumes["cybersecurity.pdf"]
    assert m1["selected_resume_name"] == "cybersecurity.pdf"
    assert m1["score"] >= 75 and m1["recommendation"] == "APPLY"
    assert m1["missing_requirements"] == [] and m1["strengths"]
    assert len(m1["resume_scores"]) == 2

    m2 = client.post(f"/api/jobs/{seeded['Backend Python Developer']['id']}/match").json()
    assert m2["selected_resume_id"] == resumes["backend.pdf"]  # requirements came from AI extraction


def test_low_score_is_skipped(client, seeded):
    m = client.post(f"/api/jobs/{seeded['Backend Python Developer']['id']}/match").json()
    assert m["recommendation"] == "APPLY"
    # a job needing skills neither resume has must be skipped and never invent evidence
    from app.database import SessionLocal
    from app.models import Job

    with SessionLocal() as s:
        job = s.get(Job, seeded["SOC Analyst"]["id"])
        job.requirements = ["Kubernetes", "AWS", "Rust", "Machine learning"]
        s.commit()
    m = client.post(f"/api/jobs/{seeded['SOC Analyst']['id']}/match").json()
    assert m["recommendation"] == "SKIP" and m["application_status"] == "SKIPPED"
    assert "kubernetes" in m["missing_requirements"]


def test_match_requires_resume(client):
    job_id = client.post("/api/jobs/discover", json={}).json()["jobs"][0]["id"]
    assert client.post(f"/api/jobs/{job_id}/match").status_code == 409
