"""Pure API boundary models; validation never grants authorization."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class BoundaryModel(BaseModel):
    """Reject unknown fields instead of silently accepting privileged input."""

    model_config = ConfigDict(extra="forbid")


Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
MessageContent = Annotated[str, StringConstraints(min_length=1, max_length=32000)]


class ChatCreate(BoundaryModel):
    """The project identity comes from the authorized route, not the body."""

    title: Name


class MessageCreate(BoundaryModel):
    """Clients submit content only; the server assigns role and identity."""

    content: MessageContent


class ProjectSummary(BoundaryModel):
    """Public project metadata deliberately excludes local filesystem roots."""

    project_id: UUID
    name: Name


class Pagination(BoundaryModel):
    """Bound the number of records returned by future list endpoints."""

    limit: Annotated[int, Field(strict=True, ge=1, le=100)] = 50
    offset: Annotated[int, Field(strict=True, ge=0, le=1000000)] = 0


class PublicError(BoundaryModel):
    """Use fixed public messages; never serialize raw exception details."""

    code: Literal["NOT_FOUND", "UNAUTHORIZED", "FORBIDDEN", "INVALID_REQUEST", "INTERNAL_ERROR"]
    message: Literal[
        "Resource unavailable",
        "Authentication required",
        "Access denied",
        "Invalid request",
        "Internal error",
    ]
    request_id: UUID


class ErrorResponse(BoundaryModel):
    """Stable error envelope for future authenticated endpoints."""

    error: PublicError
