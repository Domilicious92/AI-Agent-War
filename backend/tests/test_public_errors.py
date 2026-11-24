"""Exercise public error handlers without adding production resource routes."""

from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api_models import MessageCreate
from app.main import application
from app.public_errors import install_public_error_handlers


@pytest.fixture
def client() -> TestClient:
    test_application = FastAPI()
    install_public_error_handlers(test_application)

    @test_application.post("/message")
    def create_message(message: MessageCreate) -> dict[str, str]:
        return {"status": "ok"}

    @test_application.get("/failure/{status_code}")
    def fail(status_code: int) -> None:
        raise HTTPException(status_code=status_code, detail="/private/secret")

    @test_application.get("/unexpected")
    def unexpected() -> None:
        raise RuntimeError("/private/secret")

    return TestClient(test_application, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("status_code", "code"),
    [(401, "UNAUTHORIZED"), (403, "FORBIDDEN"), (404, "NOT_FOUND"),
     (429, "INVALID_REQUEST"), (503, "INTERNAL_ERROR")],
)
def test_http_errors_are_redacted(client: TestClient, status_code: int, code: str) -> None:
    response = client.get(f"/failure/{status_code}")
    assert response.status_code == (500 if status_code == 503 else status_code)
    assert response.json()["error"]["code"] == code
    assert "/private/secret" not in response.text
    assert response.headers["Cache-Control"] == "no-store"
    UUID(response.json()["error"]["request_id"])


def test_validation_does_not_echo_input(client: TestClient) -> None:
    response = client.post("/message", json={"content": {"secret": "private-value"}})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
    assert "private-value" not in response.text


def test_unexpected_exception_is_redacted(client: TestClient) -> None:
    response = client.get("/unexpected")
    assert response.status_code == 500
    assert response.json()["error"]["message"] == "Internal error"
    assert "/private/secret" not in response.text


def test_production_application_uses_error_envelope() -> None:
    production_client = TestClient(application)
    first = production_client.get("/missing")
    second = production_client.get("/missing")
    assert first.status_code == 404
    assert first.json()["error"]["code"] == "NOT_FOUND"
    assert first.json()["error"]["request_id"] != second.json()["error"]["request_id"]
    method_error = production_client.post("/api/health")
    assert method_error.status_code == 405
    assert "GET" in method_error.headers["Allow"]
    assert production_client.get("/api/health").json() == {"status": "ok"}
