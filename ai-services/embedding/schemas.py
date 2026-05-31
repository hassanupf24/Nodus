"""Pydantic schemas for the embedding service."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Embed a single text string."""

    text: str
    model: str | None = None  # None → use default


class BatchEmbeddingRequest(BaseModel):
    """Embed multiple texts in one request."""

    texts: list[str]
    model: str | None = None


class EmbeddingResponse(BaseModel):
    """Response containing a single embedding vector."""

    embedding: list[float]
    model: str
    dimensions: int
    tokens: int | None = None


class BatchEmbeddingResponse(BaseModel):
    """Response containing multiple embedding vectors."""

    embeddings: list[list[float]]
    model: str
    dimensions: int
    count: int
    tokens: int | None = None


class ModelInfoResponse(BaseModel):
    """Metadata about the loaded embedding model."""

    model_name: str
    dimensions: int
    max_seq_length: int
    loaded: bool = True
