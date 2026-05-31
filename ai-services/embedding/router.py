"""FastAPI router for the embedding service."""

from __future__ import annotations

from fastapi import APIRouter

from embedding.schemas import (
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelInfoResponse,
)
from embedding.service import get_embedding_service

router = APIRouter()


@router.post("", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest) -> EmbeddingResponse:
    """Generate an embedding for a single text."""
    svc = get_embedding_service()
    if request.model and request.model != svc.model_name:
        await svc.switch_model(request.model)
    vector = await svc.encode(request.text)
    return EmbeddingResponse(
        embedding=vector,
        model=svc.model_name,
        dimensions=len(vector),
    )


@router.post("/batch", response_model=BatchEmbeddingResponse)
async def create_batch_embeddings(request: BatchEmbeddingRequest) -> BatchEmbeddingResponse:
    """Generate embeddings for multiple texts."""
    svc = get_embedding_service()
    if request.model and request.model != svc.model_name:
        await svc.switch_model(request.model)
    vectors = await svc.encode_batch(request.texts)
    return BatchEmbeddingResponse(
        embeddings=vectors,
        model=svc.model_name,
        dimensions=len(vectors[0]) if vectors else 0,
        count=len(vectors),
    )


@router.get("/model", response_model=ModelInfoResponse)
async def model_info() -> ModelInfoResponse:
    """Get info about the currently loaded embedding model."""
    svc = get_embedding_service()
    if not svc.is_loaded:
        await svc.load()
    return ModelInfoResponse(
        model_name=svc.model_name,
        dimensions=svc.dimensions,
        max_seq_length=svc.max_seq_length,
    )
