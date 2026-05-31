"""Embedding pipeline — process documents → chunks → embeddings → store."""

from __future__ import annotations

import uuid
import time
from typing import Any

from embedding.service import EmbeddingService, get_embedding_service
from shared.logging_config import get_logger
from shared.vector_store import QdrantManager, get_qdrant

logger = get_logger(__name__)

DEFAULT_COLLECTION = "documents"


class EmbeddingPipeline:
    """End-to-end pipeline: takes text chunks and stores their embeddings in Qdrant."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        qdrant: QdrantManager | None = None,
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = 64,
    ) -> None:
        self._embed = embedding_service or get_embedding_service()
        self._qdrant = qdrant or get_qdrant()
        self._collection = collection
        self._batch_size = batch_size

    async def ensure_collection(self) -> None:
        """Create the target collection if it doesn't exist."""
        if not self._embed.is_loaded:
            await self._embed.load()
        self._qdrant.create_collection(
            name=self._collection,
            vector_size=self._embed.dimensions,
        )

    async def process_chunks(
        self,
        chunks: list[dict[str, Any]],
        doc_id: str | None = None,
        source: str | None = None,
    ) -> int:
        """Embed and store a list of chunks.

        Each chunk dict must have at least a ``text`` key.  Optional keys
        (``metadata``, ``chunk_index``) are preserved in the payload.

        Returns the number of points upserted.
        """
        await self.ensure_collection()

        doc_id = doc_id or str(uuid.uuid4())
        texts = [c["text"] for c in chunks]
        total = 0

        for i in range(0, len(texts), self._batch_size):
            batch_texts = texts[i: i + self._batch_size]
            batch_chunks = chunks[i: i + self._batch_size]

            vectors = await self._embed.encode_batch(batch_texts, batch_size=self._batch_size)

            payloads: list[dict[str, Any]] = []
            for idx, chunk in enumerate(batch_chunks):
                payload = {
                    "text": chunk["text"],
                    "doc_id": doc_id,
                    "source": source or "",
                    "chunk_index": chunk.get("chunk_index", i + idx),
                    "created_at": time.time(),
                }
                if "metadata" in chunk:
                    payload["metadata"] = chunk["metadata"]
                payloads.append(payload)

            n = self._qdrant.upsert(
                collection=self._collection,
                vectors=vectors,
                payloads=payloads,
            )
            total += n

        logger.info(
            "pipeline.chunks_stored",
            doc_id=doc_id,
            count=total,
            collection=self._collection,
        )
        return total

    async def process_text(
        self,
        text: str,
        doc_id: str | None = None,
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Convenience: embed a single text blob as one chunk."""
        chunk = {"text": text, "chunk_index": 0}
        if metadata:
            chunk["metadata"] = metadata
        return await self.process_chunks([chunk], doc_id=doc_id, source=source)

    async def delete_document(self, doc_id: str) -> None:
        """Remove all chunks belonging to a document."""
        self._qdrant.delete_by_filter(self._collection, "doc_id", doc_id)
        logger.info("pipeline.document_deleted", doc_id=doc_id)
