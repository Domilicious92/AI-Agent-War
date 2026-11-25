"""Contract tests for untrusted API input and public metadata."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api_models import ChatCreate, MessageCreate, Pagination, ProjectSummary, PublicError


def test_chat_title_is_normalized() -> None:
    assert ChatCreate(title="  Research  ").title == "Research"


@pytest.mark.parametrize("title", ["", "   ", "x" * 121])
def test_invalid_chat_titles_are_rejected(title: str) -> None:
    with pytest.raises(ValidationError):
        ChatCreate(title=title)


@pytest.mark.parametrize("content", ["", "x" * 32001])
def test_invalid_message_sizes_are_rejected(content: str) -> None:
    with pytest.raises(ValidationError):
        MessageCreate(content=content)


def test_client_cannot_assign_privileged_message_role() -> None:
    with pytest.raises(ValidationError):
        MessageCreate.model_validate({"content": "hello", "role": "system"})


def test_client_cannot_override_project_identity() -> None:
    with pytest.raises(ValidationError):
        ChatCreate.model_validate({"title": "chat", "project_id": str(uuid4())})


@pytest.mark.parametrize("limit", [0, 101, True, "10"])
def test_pagination_rejects_invalid_limits(limit: object) -> None:
    with pytest.raises(ValidationError):
        Pagination.model_validate({"limit": limit})


def test_project_summary_rejects_invalid_identifier() -> None:
    with pytest.raises(ValidationError):
        ProjectSummary.model_validate({"project_id": "../private", "name": "project"})


def test_public_error_rejects_raw_exception_message() -> None:
    with pytest.raises(ValidationError):
        PublicError.model_validate(
            {"code": "INTERNAL_ERROR", "message": "/private/file", "request_id": str(uuid4())}
        )


def test_project_summary_does_not_expose_root() -> None:
    summary = ProjectSummary(project_id=uuid4(), name="project")
    assert set(summary.model_dump()) == {"project_id", "name"}
