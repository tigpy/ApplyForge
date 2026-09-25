"""
Integration Tests for REST Endpoints
"""
def test_get_candidate_profile(client):
    res = client.get("/api/v1/candidate/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Aryan Singh"

def test_list_jobs(client):
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) >= 1

def test_prepare_and_approve_application(client):
    jobs = client.get("/api/v1/jobs").json()
    job_id = jobs[0]["id"]
    
    # Prepare
    prep_res = client.post("/api/v1/applications/prepare", json={"job_id": job_id})
    assert prep_res.status_code == 200
    app_data = prep_res.json()
    assert app_data["status"] == "AWAITING_REVIEW"
    app_id = app_data["id"]
    
    # Check queue
    queue_res = client.get("/api/v1/applications/queue")
    assert queue_res.status_code == 200
    queue_ids = [a["id"] for a in queue_res.json()]
    assert app_id in queue_ids
    
    # Approve
    apprv_res = client.post(f"/api/v1/applications/{app_id}/approve", params={"notes": "Looks stellar!"})
    assert apprv_res.status_code == 200
    assert apprv_res.json()["status"] == "APPROVED"
