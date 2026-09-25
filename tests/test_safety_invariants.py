"""
Tests for Zero Silent Submission Invariant
"""
def test_unapproved_application_cannot_be_submitted(client):
    jobs = client.get("/api/v1/jobs").json()
    job_id = jobs[0]["id"]
    
    prep_res = client.post("/api/v1/applications/prepare", json={"job_id": job_id})
    app_data = prep_res.json()
    app_id = app_data["id"]
    
    # Attempt submit without approval
    sub_res = client.post(f"/api/v1/applications/{app_id}/submit")
    assert sub_res.status_code == 400
    assert "Inviolable Safety Violation" in sub_res.json()["detail"]
