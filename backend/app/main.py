"""Minimal FastAPI application with no access to tools, skills, or secrets."""

from fastapi import FastAPI

application = FastAPI(
    title="AI Agent War",
    version="0.0.1",
    docs_url=None,
    redoc_url=None,
)


@application.get("/api/health")
def get_health_status() -> dict[str, str]:
    """Expose a non-sensitive health endpoint for local development and CI."""
    return {"status": "ok"}
