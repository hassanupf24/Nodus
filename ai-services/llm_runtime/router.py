"""FastAPI router for the LLM runtime service."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from llm_runtime.resource_monitor import get_resource_usage
from llm_runtime.schemas import (
    ChatRequest,
    ChatResponse,
    ModelInfo,
    ModelListResponse,
    PullRequest,
    ResourceUsage,
)
from llm_runtime.service import get_llm_service

router = APIRouter()


@router.post("/chat/completions", response_model=None)
async def chat_completions(request: ChatRequest) -> StreamingResponse | ChatResponse:
    """Chat completion endpoint with optional SSE streaming."""
    svc = get_llm_service()

    if not await svc.is_healthy():
        raise HTTPException(status_code=503, detail="Ollama server is not available")

    if request.stream:
        async def event_stream():
            async for token in svc.chat_stream(request):
                chunk = {"content": token, "done": False}
                yield f"data: {json.dumps(chunk)}\n\n"
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return await svc.chat(request)


@router.post("/completions")
async def completions(request: ChatRequest) -> dict[str, Any]:
    """Raw text completion."""
    from llm_runtime.schemas import CompletionRequest

    svc = get_llm_service()
    if not await svc.is_healthy():
        raise HTTPException(status_code=503, detail="Ollama server is not available")

    comp_req = CompletionRequest(
        model=request.model,
        prompt=request.messages[-1].content if request.messages else "",
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=False,
        stop=request.stop,
    )
    return await svc.generate(comp_req)


@router.get("/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """List all locally available models."""
    svc = get_llm_service()
    models = await svc.model_manager.list_models(refresh=True)
    return ModelListResponse(models=models)


@router.get("/models/{name}", response_model=ModelInfo)
async def get_model(name: str) -> ModelInfo:
    """Get details of a specific model."""
    svc = get_llm_service()
    model = await svc.model_manager.get_model(name)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Model {name!r} not found")
    return model


@router.post("/models/pull")
async def pull_model(request: PullRequest) -> StreamingResponse:
    """Pull/download a model from the Ollama registry."""
    svc = get_llm_service()

    async def progress_stream():
        async for progress in svc.model_manager.pull_model(request.name):
            yield f"data: {progress.model_dump_json()}\n\n"

    return StreamingResponse(progress_stream(), media_type="text/event-stream")


@router.delete("/models/{name}")
async def delete_model(name: str) -> dict[str, Any]:
    """Delete a local model."""
    svc = get_llm_service()
    deleted = await svc.model_manager.delete_model(name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Model {name!r} not found or could not be deleted")
    return {"status": "deleted", "model": name}


@router.get("/resources", response_model=ResourceUsage)
async def resources() -> ResourceUsage:
    """Get current system resource usage."""
    return await get_resource_usage()
