"""Qdrant vector store management — embedded mode, collection CRUD, search."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from shared.logging_config import get_logger

logger = get_logger(__name__)


class QdrantManager:
    """Thin wrapper around the Qdrant client for embedded-mode usage."""

    def __init__(self, path: Path | str | None = None) -> None:
        if path:
            self._path = Path(path)
            self._path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(self._path))
        else:
            # In-memory (useful for tests)
            self._path = None
            self._client = QdrantClient(location=":memory:")
        logger.info("qdrant.initialized", path=str(path))

    @property
    def client(self) -> QdrantClient:
        return self._client

    # ── Collection management ──────────────────────────────
    def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        on_disk: bool = True,
    ) -> None:
        """Create a new collection if it doesn't already exist."""
        existing = {c.name for c in self._client.get_collections().collections}
        if name in existing:
            logger.debug("qdrant.collection_exists", name=name)
            return
        self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=distance, on_disk=on_disk),
        )
        # Create payload indexes for common filter fields
        for field in ("source", "doc_id", "chunk_index"):
            self._client.create_payload_index(
                collection_name=name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        self._client.create_payload_index(
            collection_name=name,
            field_name="created_at",
            field_schema=models.PayloadSchemaType.FLOAT,
        )
        logger.info("qdrant.collection_created", name=name, vector_size=vector_size)

    def delete_collection(self, name: str) -> bool:
        """Delete a collection. Returns True if it existed."""
        existing = {c.name for c in self._client.get_collections().collections}
        if name not in existing:
            return False
        self._client.delete_collection(collection_name=name)
        logger.info("qdrant.collection_deleted", name=name)
        return True

    def list_collections(self) -> list[str]:
        return [c.name for c in self._client.get_collections().collections]

    def collection_info(self, name: str) -> dict[str, Any]:
        info = self._client.get_collection(collection_name=name)
        return {
            "name": name,
            "vector_size": info.config.params.vectors.size,  # type: ignore[union-attr]
            "points_count": info.points_count,
            "status": info.status.value,
        }

    # ── CRUD ────────────────────────────────────────────────
    def upsert(
        self,
        collection: str,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> int:
        """Upsert vectors with payloads. Returns number of points upserted."""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in vectors]
        points = [
            PointStruct(id=uid, vector=vec, payload=pay)
            for uid, vec, pay in zip(ids, vectors, payloads, strict=True)
        ]
        self._client.upsert(collection_name=collection, points=points)
        logger.debug("qdrant.upserted", collection=collection, count=len(points))
        return len(points)

    def search(
        self,
        collection: str,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic vector search with optional filters."""
        qdrant_filter: Filter | None = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            qdrant_filter = Filter(must=must_conditions)

        results = self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter,
        )
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload,
            }
            for r in results
        ]

    def delete_by_filter(self, collection: str, key: str, value: str) -> None:
        """Delete all points matching a payload filter."""
        self._client.delete(
            collection_name=collection,
            points_selector=models.FilterSelector(
                filter=Filter(must=[FieldCondition(key=key, match=MatchValue(value=value))])
            ),
        )
        logger.info("qdrant.deleted_by_filter", collection=collection, key=key, value=value)

    def count(self, collection: str) -> int:
        info = self._client.get_collection(collection_name=collection)
        return info.points_count or 0

    def close(self) -> None:
        self._client.close()
        logger.info("qdrant.closed")


# ── Singleton ──────────────────────────────────────────────
_manager: QdrantManager | None = None


def get_qdrant(path: Path | str | None = None) -> QdrantManager:
    global _manager  # noqa: PLW0603
    if _manager is None:
        from shared.config import get_settings
        _manager = QdrantManager(path or get_settings().qdrant_path)
    return _manager
