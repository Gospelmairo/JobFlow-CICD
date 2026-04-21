from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job():
    with patch("main.r") as mock_r:
        mock_r.hset.return_value = True
        mock_r.lpush.return_value = 1
        response = client.post("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert len(data["job_id"]) > 0


def test_get_job_found():
    with patch("main.r") as mock_r:
        mock_r.hget.return_value = "queued"
        response = client.get("/jobs/test-job-id")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["job_id"] == "test-job-id"


def test_get_job_not_found():
    with patch("main.r") as mock_r:
        mock_r.hget.return_value = None
        response = client.get("/jobs/nonexistent")
        assert response.status_code == 404


def test_create_job_hset_before_lpush():
    """Race condition fix: metadata must be stored before job is queued."""
    with patch("main.r") as mock_r:
        call_order = []
        mock_r.hset.side_effect = lambda *a, **k: call_order.append("hset")
        mock_r.lpush.side_effect = lambda *a, **k: call_order.append("lpush")
        client.post("/jobs")
        assert call_order == ["hset", "lpush"]
