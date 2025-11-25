from fastapi.testclient import TestClient

from app.main import create_app


def test_create_and_query_session():
    app = create_app()
    client = TestClient(app)

    # create session with duration and specific now
    r = client.post("/api/v1/sessions", json={"duration_ms": 5000, "now_ms": 100000})
    assert r.status_code == 200
    body = r.json()
    sid = body["id"]
    assert body["status"] == "running"
    assert body["remaining_ms"] == 5000

    # query with later now to compute remaining
    r2 = client.get(f"/api/v1/sessions/{sid}", params={"now_ms": 100100})
    assert r2.status_code == 200
    assert r2.json()["remaining_ms"] == 4900


def test_pause_and_resume_via_api():
    app = create_app()
    client = TestClient(app)

    r = client.post("/api/v1/sessions", json={"duration_ms": 60000, "now_ms": 0})
    sid = r.json()["id"]

    # advance 30000 and pause
    r_pause = client.patch(f"/api/v1/sessions/{sid}", json={"action": "pause", "now_ms": 30000})
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "paused"
    assert r_pause.json()["remaining_ms"] == 30000

    # while paused, advancing time should not reduce remaining
    r_get = client.get(f"/api/v1/sessions/{sid}", params={"now_ms": 60000})
    assert r_get.status_code == 200
    assert r_get.json()["remaining_ms"] == 30000

    # resume at 60000, advance 20000 -> remaining should be 10000
    r_resume = client.patch(f"/api/v1/sessions/{sid}", json={"action": "resume", "now_ms": 60000})
    assert r_resume.status_code == 200
    r_after = client.get(f"/api/v1/sessions/{sid}", params={"now_ms": 80000})
    assert r_after.json()["remaining_ms"] == 10000
