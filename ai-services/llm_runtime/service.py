"""LLM Service — high-level interface for chat and completion via Ollama."""

from __future__ import annotations

from typing import Any, AsyncIterator

from llm_runtime.model_manager import ModelManager
from llm_runtime.ollama_client import OllamaClient
from llm_runtime.schemas import ChatMessage, ChatRequest, ChatResponse, CompletionRequest, Role
from shared.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Manages Ollama connection and provides chat / completion methods."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 120.0) -> None:
        self._client = OllamaClient(base_url=base_url, timeout=timeout)
        self._model_manager = ModelManager(self._client)

    @property
    def client(self) -> OllamaClient:
        return self._client

    @property
    def model_manager(self) -> ModelManager:
        return self._model_manager

    async def close(self) -> None:
        await self._client.close()

    async def is_healthy(self) -> bool:
        return await self._client.is_healthy()

    # ── Chat (streaming) ──────────────────────────────────

    async def chat_stream(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat tokens as an async iterator of content strings."""
        messages = [{"role": m.role.value, "content": m.content} for m in request.messages]

        if request.system:
            messages.insert(0, {"role": "system", "content": request.system})

        logger.info("llm.chat_stream.start", model=request.model, message_count=len(messages))

        response = await self._client.chat(
            model=request.model,
            messages=messages,
            stream=True,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )

        async for chunk in response:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    # ── Chat (non-streaming) ──────────────────────────────

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Single-shot chat completion (no streaming)."""
        messages = [{"role": m.role.value, "content": m.content} for m in request.messages]

        if request.system:
            messages.insert(0, {"role": "system", "content": request.system})

        logger.info("llm.chat.start", model=request.model, message_count=len(messages))

        result = await self._client.chat(
            model=request.model,
            messages=messages,
            stream=False,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )

        msg = result.get("message", {})
        eval_count = result.get("eval_count", 0)
        eval_duration = result.get("eval_duration", 0)
        tps = (eval_count / (eval_duration / 1e9)) if eval_duration else None

        return ChatResponse(
            model=request.model,
            message=ChatMessage(role=Role(msg.get("role", "assistant")), content=msg.get("content", "")),
            done=result.get("done", True),
            total_duration=result.get("total_duration"),
            eval_count=eval_count,
            eval_duration=eval_duration,
            tokens_per_second=round(tps, 1) if tps else None,
        )

    # ── Raw completion (streaming) ────────────────────────

    async def generate_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """Stream raw completion tokens."""
        logger.info("llm.generate_stream.start", model=request.model)
        response = await self._client.generate(
            model=request.model,
            prompt=request.prompt,
            stream=True,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )
        async for chunk in response:
            content = chunk.get("response", "")
            if content:
                yield content

    # ── Raw completion (non-streaming) ────────────────────

    async def generate(self, request: CompletionRequest) -> dict[str, Any]:
        """Single-shot text completion."""
        result = await self._client.generate(
            model=request.model,
            prompt=request.prompt,
            stream=False,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )
        return result


# ── Singleton ─────────────────────────────────────────────
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service  # noqa: PLW0603
    if _llm_service is None:
        from shared.config import get_settings
        s = get_settings()
        _llm_service = LLMService(base_url=s.ollama_base_url, timeout=s.request_timeout)
    return _llm_service
