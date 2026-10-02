import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from app import app


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_readiness():
    client = app.test_client()
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


def test_status():
    client = app.test_client()
    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.get_json()

    assert data["service"] == "cicd-automated-deployment"
    assert data["status"] == "running"
    assert "deployment" in data


def test_system_metrics():
    client = app.test_client()
    response = client.get("/api/system")

    assert response.status_code == 200

    data = response.get_json()

    assert "hostname" in data
    assert "cpu_cores" in data
    assert "memory_used_mb" in data
    assert "uptime_seconds" in data


def test_version_metadata():
    client = app.test_client()
    response = client.get("/version")

    assert response.status_code == 200

    data = response.get_json()

    assert "environment" in data
    assert "version" in data
    assert "build_number" in data
    assert "git_commit" in data
    assert "deployed_by" in data
