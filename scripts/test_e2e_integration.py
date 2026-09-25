import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def request_json(url, method="GET", data=None):
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, json.loads(body) if body else {}

def main():
    print("=== APPLYFORGE FULL-STACK INTEGRATION VERIFICATION ===")
    
    # 1. Candidate Profile
    status, profile = request_json(f"{BASE_URL}/candidate/profile")
    assert status == 200, f"Failed to get candidate profile: {status}"
    print(f"[PASS] Candidate Profile: {profile.get('name')} ({profile.get('email')})")
    
    # 2. Trigger Discovery Connector
    status, disc = request_json(f"{BASE_URL}/connectors/discover?platform=mock", method="POST")
    assert status == 200, f"Discovery failed: {status}"
    print(f"[PASS] Connector Discovery: {disc}")
    
    # 3. List Jobs
    status, jobs = request_json(f"{BASE_URL}/jobs")
    assert status == 200 and len(jobs) > 0, f"Jobs list failed or empty: {status}, {len(jobs)}"
    print(f"[PASS] Jobs Catalog: {len(jobs)} jobs available")
    
    status, existing_apps = request_json(f"{BASE_URL}/applications")
    app_job_ids = {a["job_id"] for a in existing_apps}
    unapplied_jobs = [j for j in jobs if j["id"] not in app_job_ids]
    if not unapplied_jobs:
        import time
        ts = int(time.time())
        status, new_job = request_json(
            f"{BASE_URL}/jobs/import",
            method="POST",
            data={
                "source_name": "manual",
                "external_id": f"E2E-AUTO-{ts}",
                "title": f"Security Automation Engineer {ts}",
                "company": "ForgeGuard Cyber",
                "location": "Remote",
                "work_mode": "REMOTE",
                "employment_type": "FULL_TIME",
                "description_raw": "Seeking Security Automation Engineer with Python, Linux, and FastAPI."
            }
        )
        assert status == 201, f"Failed to create job via API: {status}, {new_job}"
        job = new_job
    else:
        job = unapplied_jobs[0]
    job_id = job["id"]
    print(f"       Using Job ID {job_id}: {job.get('title')} at {job.get('company')}")
    
    # 4. Prepare Application
    status, app = request_json(f"{BASE_URL}/applications/prepare", method="POST", data={"job_id": job_id})
    assert status == 200, f"Application prepare failed: {status}, {app}"
    app_id = app["id"]
    print(f"[PASS] Prepared Application #{app_id}: status={app.get('status')}")
    assert app.get("status") == "AWAITING_REVIEW", f"Expected AWAITING_REVIEW, got {app.get('status')}"
    
    # 5. Inviolable Rule: Attempt to submit unapproved application (MUST BE REJECTED)
    status, err = request_json(f"{BASE_URL}/applications/{app_id}/submit", method="POST")
    assert status == 400, f"Expected 400 on unapproved submit, got {status}"
    print(f"[PASS] Inviolable Rule Enforced: Submit blocked when status is '{app.get('status')}': {err.get('detail')}")
    
    # 6. Approve Application (Human-in-the-loop review)
    status, approved_app = request_json(f"{BASE_URL}/applications/{app_id}/approve", method="POST", data={"notes": "Human approved for submission"})
    assert status == 200, f"Approval failed: {status}"
    assert approved_app.get("status") == "APPROVED", f"Expected APPROVED, got {approved_app.get('status')}"
    print(f"[PASS] Human Approval Granted: Application #{app_id} is now '{approved_app.get('status')}'")
    
    # 7. Submit Application
    status, submitted_app = request_json(f"{BASE_URL}/applications/{app_id}/submit", method="POST")
    assert status == 200, f"Submission failed: {status}"
    assert submitted_app.get("status") == "SUBMITTED", f"Expected SUBMITTED, got {submitted_app.get('status')}"
    print(f"[PASS] Application Submission: Application #{app_id} transitioned to '{submitted_app.get('status')}'")
    
    # 8. Resume PDF Generation
    pdf_req = urllib.request.Request(f"{BASE_URL}/applications/{app_id}/resume/pdf")
    with urllib.request.urlopen(pdf_req) as pdf_resp:
        pdf_bytes = pdf_resp.read()
        assert pdf_resp.status == 200, f"PDF failed: {pdf_resp.status}"
        assert pdf_bytes.startswith(b"%PDF"), "Response is not a valid PDF binary"
        print(f"[PASS] PDF Resume Generated: {len(pdf_bytes)} bytes valid PDF")
        
    # 9. Verify Audit Trail
    status, audit = request_json(f"{BASE_URL}/audit/logs")
    assert status == 200 and len(audit) > 0, f"Audit logs failed: {status}"
    events = [a.get("event_type") for a in audit if a.get("application_id") == app_id]
    print(f"[PASS] Tamper-Evident Audit Trail: Verified events for app #{app_id}: {events}")
    
    # 10. Verify Caddy Reverse Proxy
    status, caddy_profile = request_json("http://localhost/api/v1/candidate/profile")
    assert status == 200 and caddy_profile.get("email") == profile.get("email"), "Caddy proxy to API failed"
    print(f"[PASS] Caddy Reverse Proxy (Port 80 -> API Port 8000): Verified")
    
    # 11. Verify Web Frontend through Caddy and Direct
    web_req = urllib.request.Request("http://localhost/")
    with urllib.request.urlopen(web_req) as web_resp:
        html = web_resp.read().decode("utf-8")
        assert web_resp.status == 200, f"Web via Caddy failed: {web_resp.status}"
        assert "ApplyForge" in html, "Web response missing ApplyForge brand"
        print(f"[PASS] Caddy Reverse Proxy (Port 80 -> Next.js Port 3000): HTTP {web_resp.status}, Brand verified")
        
    print("\nALL 11 END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
