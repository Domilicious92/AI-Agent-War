"""Smoke tests for the intentionally limited P0 backend."""

from fastapi.testclient import TestClient

from app.main import application


def test_health_endpoint_returns_expected_status() -> None:
    """The status route is deterministic and does not require API credentials."""
    client = TestClient(application)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extension_execution_endpoint_is_not_exposed() -> None:
    """No plugin execution surface is permitted before the security gate exists."""
    client = TestClient(application)

    response = client.post("/api/extensions/execute")

    assert response.status_code == 404
