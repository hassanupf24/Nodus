"""Async HTTP client for the Ollama API (localhost:11434)."""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from shared.logging_config import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Async wrapper around the Ollama HTTP API.

    Connects to the Ollama server running at *base_url* (default
    ``http://localhost:11434``).
    """

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(self._timeout, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # ── Models ──────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        """GET /api/tags → list of locally available models."""
        client = await self._get_client()
        resp = await client.get("/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return data.get("models", [])

    async def show_model(self, name: str) -> dict[str, Any]:
        """POST /api/show → model details."""
        client = await self._get_client()
        resp = await client.post("/api/show", json={"name": name})
        resp.raise_for_status()
        return resp.json()

    async def pull_model(self, name: str) -> AsyncIterator[dict[str, Any]]:
        """POST /api/pull → stream download progress."""
        client = await self._get_client()
        async with client.stream("POST", "/api/pull", json={"name": name, "stream": True}) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    import json
                    yield json.loads(line)

    async def delete_model(self, name: str) -> bool:
        """DELETE /api/delete → remove model."""
        client = await self._get_client()
        resp = await client.request("DELETE", "/api/delete", json={"name": name})
        return resp.status_code == 200

    # ── Generate (raw completion) ──────────────────────────

    async def generate(
        self,
        model: str,
        prompt: str,
        *,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]] | dict[str, Any]:
        """POST /api/generate — raw text completion."""
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop:
            payload["options"]["stop"] = stop

        client = await self._get_client()

        if stream:
            return self._stream_response(client, "/api/generate", payload)

        resp = await client.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()

    # ── Chat ──────────────────────────────────────────────

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]] | dict[str, Any]:
        """POST /api/chat — multi-turn chat."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop:
            payload["options"]["stop"] = stop

        client = await self._get_client()

        if stream:
            return self._stream_response(client, "/api/chat", payload)

        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()

    # ── Embeddings ────────────────────────────────────────

    async def embeddings(self, model: str, input_text: str | list[str]) -> list[list[float]]:
        """POST /api/embed → vector embeddings."""
        client = await self._get_client()
        if isinstance(input_text, str):
            input_text = [input_text]
        resp = await client.post("/api/embed", json={"model": model, "input": input_text})
        resp.raise_for_status()
        data = resp.json()
        return data.get("embeddings", [])

    # ── Health ────────────────────────────────────────────

    async def is_healthy(self) -> bool:
        """Quick health check."""
        try:
            client = await self._get_client()
            resp = await client.get("/")
            return resp.status_code == 200
        except Exception:
            return False

    # ── Streaming helper ──────────────────────────────────

    async def _stream_response(
        self, client: httpx.AsyncClient, path: str, payload: dict[str, Any]
    ) -> AsyncIterator[dict[str, Any]]:
        import json

        async with client.stream("POST", path, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    yield json.loads(line)
