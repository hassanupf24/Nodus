"""Embedding service — loads sentence-transformer models and encodes text to vectors."""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from shared.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Manages a sentence-transformers model for generating embeddings.

    The heavy encode() call runs in a thread-pool so the event loop stays free.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str | None = None) -> None:
        self._model_name = model_name
        self._device = device
        self._model: Any = None  # SentenceTransformer instance
        self._lock = asyncio.Lock()

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        if self._model is None:
            return 0
        return self._model.get_sentence_embedding_dimension()

    @property
    def max_seq_length(self) -> int:
        if self._model is None:
            return 0
        return self._model.max_seq_length

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    async def load(self) -> None:
        """Load the sentence-transformer model (thread-safe, idempotent)."""
        async with self._lock:
            if self._model is not None:
                return
            logger.info("embedding.loading_model", model=self._model_name)
            loop = asyncio.get_running_loop()
            self._model = await loop.run_in_executor(None, self._load_model_sync)
            logger.info(
                "embedding.model_loaded",
                model=self._model_name,
                dimensions=self.dimensions,
                max_seq_length=self.max_seq_length,
            )

    def _load_model_sync(self) -> Any:
        from sentence_transformers import SentenceTransformer

        kwargs: dict[str, Any] = {}
        if self._device:
            kwargs["device"] = self._device
        return SentenceTransformer(self._model_name, **kwargs)

    async def encode(self, text: str) -> list[float]:
        """Encode a single text to a vector."""
        if self._model is None:
            await self.load()
        loop = asyncio.get_running_loop()
        vector = await loop.run_in_executor(
            None, partial(self._model.encode, text, normalize_embeddings=True)
        )
        return vector.tolist()

    async def encode_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Encode a batch of texts to vectors."""
        if self._model is None:
            await self.load()
        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(
            None,
            partial(
                self._model.encode,
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
            ),
        )
        return vectors.tolist()

    async def unload(self) -> None:
        """Release the model from memory."""
        async with self._lock:
            if self._model is not None:
                del self._model
                self._model = None
                logger.info("embedding.model_unloaded", model=self._model_name)

    async def switch_model(self, model_name: str) -> None:
        """Unload current model and load a new one."""
        await self.unload()
        self._model_name = model_name
        await self.load()


# ── Singleton ─────────────────────────────────────────────
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service  # noqa: PLW0603
    if _embedding_service is None:
        from shared.config import get_settings
        _embedding_service = EmbeddingService(model_name=get_settings().embedding_model)
    return _embedding_service
