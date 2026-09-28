def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["ai_provider"] == "mock"
    assert body["application_connector"] == "mock"
