from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "status": "ok",
        "service": "Career Copilot API Gateway",
        "version": "0.1.0",
        "environment": "development",
    }