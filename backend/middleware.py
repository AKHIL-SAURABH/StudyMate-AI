"""
StudyMate AI — FastAPI Middleware.

Provides CORS configuration, request logging with correlation IDs,
and global exception handling middleware.
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.exceptions import StudyMateError
from utils.logger import get_logger, set_correlation_id, generate_correlation_id

logger = get_logger("middleware")


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI app.

    Allows Streamlit frontend (typically localhost:8501) to access the API.

    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware that logs each request with timing and correlation ID.

    Args:
        request: Incoming HTTP request.
        call_next: Next middleware or route handler.

    Returns:
        HTTP response with correlation ID header.
    """
    # Generate or extract correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
    set_correlation_id(correlation_id)

    start_time = time.perf_counter()
    method = request.method
    path = request.url.path

    logger.info("-> %s %s", method, path)

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "<- %s %s [%d] %.1fms",
            method,
            path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error("FAIL %s %s failed after %.1fms: %s", method, path, duration_ms, exc)
        raise


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.

    Converts StudyMateError instances to structured JSON responses.
    All other exceptions return a generic 500 error.

    Args:
        request: Incoming HTTP request.
        exc: The unhandled exception.

    Returns:
        JSONResponse with error details.
    """
    if isinstance(exc, StudyMateError):
        status_code = _error_to_status_code(exc.code)
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            },
        )

    # Unexpected errors
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
            },
        },
    )


def _error_to_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes."""
    mapping = {
        "AUTH_ERROR": 401,
        "USER_NOT_FOUND": 404,
        "USER_EXISTS": 409,
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 422,
        "AGENT_ERROR": 500,
        "LLM_ERROR": 502,
        "TOOL_ERROR": 500,
        "MAX_ITERATIONS": 500,
        "JSON_PARSE_ERROR": 500,
        "MCP_CONNECTION_ERROR": 503,
        "MCP_TOOL_NOT_FOUND": 404,
        "DATABASE_ERROR": 500,
        "INTERNAL_ERROR": 500,
    }
    return mapping.get(error_code, 500)


def setup_middleware(app: FastAPI) -> None:
    """
    Apply all middleware to the FastAPI application.

    Args:
        app: FastAPI application instance.
    """
    setup_cors(app)
    app.middleware("http")(request_logging_middleware)
    app.add_exception_handler(StudyMateError, global_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)
