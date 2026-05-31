"""Pydantic models for the LLM runtime service."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    """Request body for chat completions."""

    model: str = "llama3.2"
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32768)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    stream: bool = True
    stop: list[str] | None = None
    system: str | None = None


class CompletionRequest(BaseModel):
    """Request body for raw text completions."""

    model: str = "llama3.2"
    prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32768)
    stream: bool = True
    stop: list[str] | None = None


class ChatResponse(BaseModel):
    """Non-streaming chat response."""

    model: str
    message: ChatMessage
    done: bool = True
    total_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None
    tokens_per_second: float | None = None


class StreamChunk(BaseModel):
    """A single SSE chunk during streaming."""

    model: str
    content: str
    done: bool = False


class ModelInfo(BaseModel):
    """Information about an available model."""

    name: str
    model: str
    modified_at: datetime | None = None
    size: int = 0  # bytes
    digest: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None
    family: str | None = None


class ModelListResponse(BaseModel):
    models: list[ModelInfo] = Field(default_factory=list)


class PullRequest(BaseModel):
    name: str
    stream: bool = True


class PullProgress(BaseModel):
    status: str
    digest: str | None = None
    total: int | None = None
    completed: int | None = None
    percent: float | None = None


class ResourceUsage(BaseModel):
    """System resource snapshot."""

    cpu_percent: float
    ram_total_gb: float
    ram_used_gb: float
    ram_available_gb: float
    gpu_name: str | None = None
    gpu_vram_total_mb: int | None = None
    gpu_vram_used_mb: int | None = None
    gpu_vram_free_mb: int | None = None
    gpu_utilization_percent: float | None = None


class EmbeddingRequest(BaseModel):
    """Request embeddings from Ollama."""

    model: str = "nomic-embed-text"
    input: str | list[str]


class EmbeddingResponse(BaseModel):
    model: str
    embeddings: list[list[float]]
