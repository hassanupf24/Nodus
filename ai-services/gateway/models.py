"""Shared Pydantic request / response models used across the gateway."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Generic wrappers ──────────────────────────────────────


class StatusEnum(str, Enum):
    OK = "ok"
    ERROR = "error"
    PROCESSING = "processing"


class APIResponse(BaseModel):
    """Standard envelope for all API responses."""

    status: StatusEnum = StatusEnum.OK
    data: Any | None = None
    message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class ErrorResponse(BaseModel):
    status: StatusEnum = StatusEnum.ERROR
    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class PaginatedResponse(BaseModel):
    status: StatusEnum = StatusEnum.OK
    data: list[Any] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 20
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Health ────────────────────────────────────────────────


class ServiceHealth(BaseModel):
    name: str
    status: str = "healthy"
    latency_ms: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ResourceUsage(BaseModel):
    cpu_percent: float = 0.0
    ram_used_mb: float = 0.0
    ram_total_mb: float = 0.0
    gpu_percent: float | None = None
    gpu_vram_used_mb: float | None = None
    gpu_vram_total_mb: float | None = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    services: list[ServiceHealth] = Field(default_factory=list)
    uptime_seconds: float = 0.0
    resources: ResourceUsage = Field(default_factory=ResourceUsage)
