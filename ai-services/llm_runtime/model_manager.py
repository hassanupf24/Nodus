"""Model manager — tracks available models, downloads, validates, reports VRAM/RAM."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator

from llm_runtime.ollama_client import OllamaClient
from llm_runtime.schemas import ModelInfo, PullProgress
from shared.logging_config import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages the lifecycle of LLM models via Ollama."""

    def __init__(self, client: OllamaClient) -> None:
        self._client = client
        self._model_cache: dict[str, ModelInfo] = {}

    async def list_models(self, refresh: bool = False) -> list[ModelInfo]:
        """Return cached or freshly-fetched model list."""
        if not self._model_cache or refresh:
            raw = await self._client.list_models()
            self._model_cache = {}
            for m in raw:
                info = ModelInfo(
                    name=m.get("name", ""),
                    model=m.get("model", m.get("name", "")),
                    modified_at=m.get("modified_at"),
                    size=m.get("size", 0),
                    digest=m.get("digest"),
                    parameter_size=m.get("details", {}).get("parameter_size"),
                    quantization_level=m.get("details", {}).get("quantization_level"),
                    family=m.get("details", {}).get("family"),
                )
                self._model_cache[info.name] = info
        return list(self._model_cache.values())

    async def get_model(self, name: str) -> ModelInfo | None:
        models = await self.list_models()
        return self._model_cache.get(name)

    async def is_available(self, name: str) -> bool:
        models = await self.list_models()
        return name in self._model_cache

    async def pull_model(self, name: str) -> AsyncIterator[PullProgress]:
        """Stream download progress for a model."""
        logger.info("model_manager.pulling", model=name)
        async for chunk in self._client.pull_model(name):
            total = chunk.get("total", 0)
            completed = chunk.get("completed", 0)
            percent = (completed / total * 100) if total else None
            yield PullProgress(
                status=chunk.get("status", ""),
                digest=chunk.get("digest"),
                total=total or None,
                completed=completed or None,
                percent=round(percent, 1) if percent else None,
            )
        # Refresh cache
        await self.list_models(refresh=True)
        logger.info("model_manager.pulled", model=name)

    async def delete_model(self, name: str) -> bool:
        """Remove a model from Ollama."""
        result = await self._client.delete_model(name)
        if result:
            self._model_cache.pop(name, None)
            logger.info("model_manager.deleted", model=name)
        return result

    async def validate_model(self, name: str) -> dict[str, Any]:
        """Show model details to verify integrity."""
        try:
            details = await self._client.show_model(name)
            return {"valid": True, "details": details}
        except Exception as exc:
            return {"valid": False, "error": str(exc)}

    def estimate_memory(self, model_info: ModelInfo) -> dict[str, Any]:
        """Rough estimate of memory needed based on model size and quant level."""
        size_gb = model_info.size / (1024**3) if model_info.size else 0
        # Rough heuristic: loaded model ≈ 1.2× disk size for quantized
        estimated_ram_gb = round(size_gb * 1.2, 2)
        return {
            "model": model_info.name,
            "disk_size_gb": round(size_gb, 2),
            "estimated_ram_gb": estimated_ram_gb,
            "quantization": model_info.quantization_level,
        }
