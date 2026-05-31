"""Request logging, timing, and error-handling middleware."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from shared.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach a request ID, log every request, and record latency."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()

        logger.info(
            "http.request.start",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "http.request.error",
                method=request.method,
                path=request.url.path,
                request_id=request_id,
                elapsed_ms=round(elapsed_ms, 2),
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

        logger.info(
            "http.request.end",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            request_id=request_id,
            elapsed_ms=round(elapsed_ms, 2),
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return a JSON 500 response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("http.unhandled_error", error=str(exc))
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error": "Internal Server Error",
                    "detail": str(exc) if getattr(request.app.state, "debug", False) else None,
                },
            )


def install_middleware(app: FastAPI) -> None:
    """Add all custom middleware to the FastAPI application."""
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
