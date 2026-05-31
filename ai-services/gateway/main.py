"""Nodus API Gateway — FastAPI application entry-point."""

from __future__ import annotations

import time
import sys
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gateway.config import get_gateway_settings
from gateway.middleware import install_middleware
from gateway.models import APIResponse, ErrorResponse, HealthResponse, ServiceHealth
from gateway.router import register_routes
from shared.config import get_settings
from shared.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

_start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle hook."""
    global _start_time  # noqa: PLW0603
    _start_time = time.time()

    settings = get_settings()
    gw = get_gateway_settings()
    setup_logging(log_level=gw.log_level, json_output=gw.log_json)
    settings.ensure_dirs()

    logger.info(
        "gateway.starting",
        host=gw.host,
        port=gw.port,
        debug=gw.debug,
    )

    yield  # ── app is running ──

    # Graceful shutdown
    from shared.database import _default_db
    from shared.vector_store import _manager

    if _default_db is not None:
        await _default_db.close()
    if _manager is not None:
        _manager.close()
    logger.info("gateway.shutdown")


def create_app() -> FastAPI:
    """Factory that builds the fully-configured FastAPI application."""
    gw = get_gateway_settings()

    app = FastAPI(
        title="Nodus AI Gateway",
        description="Local-First Private AI Memory Infrastructure",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if gw.debug else None,
        redoc_url="/redoc" if gw.debug else None,
    )
    app.state.debug = gw.debug

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=gw.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (logging, error handling)
    install_middleware(app)

    # Mount all sub-service routers
    register_routes(app)

    # ── Root endpoints ─────────────────────────────────
    @app.get("/", response_model=APIResponse)
    async def root() -> APIResponse:
        return APIResponse(data={"service": "Nodus AI Gateway", "version": "0.1.0"})

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        uptime = time.time() - _start_time
        services: list[ServiceHealth] = []

        # Check Ollama
        try:
            import httpx

            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{get_settings().ollama_base_url}/api/tags")
                services.append(ServiceHealth(name="ollama", status="healthy", latency_ms=r.elapsed.total_seconds() * 1000))
        except Exception:
            services.append(ServiceHealth(name="ollama", status="unavailable"))

        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            resources = {
                "cpu_percent": cpu_percent,
                "ram_used_mb": mem.used / (1024 * 1024),
                "ram_total_mb": mem.total / (1024 * 1024),
            }
        except ImportError:
            resources = {}

        return HealthResponse(uptime_seconds=round(uptime, 1), services=services, resources=resources)

    return app


# ── Exception handlers ─────────────────────────────────────

app = create_app()


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error="Validation Error", detail=str(exc)).model_dump(mode="json"),
    )


@app.exception_handler(FileNotFoundError)
async def not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(error="Not Found", detail=str(exc)).model_dump(mode="json"),
    )


@app.exception_handler(PermissionError)
async def permission_handler(request: Request, exc: PermissionError) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content=ErrorResponse(error="Forbidden", detail=str(exc)).model_dump(mode="json"),
    )


if __name__ == "__main__":
    import uvicorn

    gw = get_gateway_settings()
    uvicorn.run("gateway.main:app", host=gw.host, port=gw.port, reload=gw.debug)
