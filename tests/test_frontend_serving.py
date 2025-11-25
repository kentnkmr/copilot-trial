from fastapi.testclient import TestClient
from app.main import create_app


def test_frontend_index_served():
    app = create_app()
    client = TestClient(app)
    r = client.get("/")
    # index.html should exist and contain the title
    assert r.status_code == 200
    assert "Pomodoro Timer — Minimal" in r.text
