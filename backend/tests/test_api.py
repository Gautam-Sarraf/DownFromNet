import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ffmpeg_available" in data


def test_system_info_endpoint():
    response = client.get("/api/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "supported_video_formats" in data


def test_analyze_empty_url_validation():
    response = client.post("/api/analyze", json={"url": ""})
    assert response.status_code in [400, 422]


def test_analyze_ssrf_blocked():
    response = client.post("/api/analyze", json={"url": "http://127.0.0.1:8000/secret"})
    assert response.status_code == 403
    data = response.json()
    assert "restricted" in data.get("detail", "").lower() or "local" in data.get("detail", "").lower()
