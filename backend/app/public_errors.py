"""Map HTTP failures to fixed public messages without exposing request data."""

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api_models import ErrorResponse, PublicError


def public_error_response(status_code: int) -> JSONResponse:
    """Generate a fresh server-owned correlation identifier for each error."""
    if status_code == 401:
        error = PublicError(code="UNAUTHORIZED", message="Authentication required", request_id=uuid4())
    elif status_code == 403:
        error = PublicError(code="FORBIDDEN", message="Access denied", request_id=uuid4())
    elif status_code == 404:
        error = PublicError(code="NOT_FOUND", message="Resource unavailable", request_id=uuid4())
    elif 400 <= status_code < 500:
        error = PublicError(code="INVALID_REQUEST", message="Invalid request", request_id=uuid4())
    else:
        status_code = 500
        error = PublicError(code="INTERNAL_ERROR", message="Internal error", request_id=uuid4())
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error).model_dump(mode="json"),
        headers={"Cache-Control": "no-store"},
    )


def install_public_error_handlers(application: FastAPI) -> None:
    """Register handlers before exposing any authenticated resource routes."""

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exception: RequestValidationError) -> JSONResponse:
        return public_error_response(422)

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exception: HTTPException) -> JSONResponse:
        response = public_error_response(exception.status_code)
        # Preserve protocol headers only; never forward arbitrary exception headers.
        if exception.status_code == 405 and exception.headers:
            for name, value in exception.headers.items():
                if name.lower() == "allow":
                    response.headers["Allow"] = value
        return response

    @application.exception_handler(Exception)
    async def internal_error(request: Request, exception: Exception) -> JSONResponse:
        return public_error_response(500)
