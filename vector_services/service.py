import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from vector_services.schemas import VectorPoint

class VectorService:
    """Manages the embedded Qdrant vector database storage layer."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        if storage_path:
            self._path = Path(storage_path)
            self._path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(self._path))
        else:
            # Fallback to in-memory mode for dynamic testing
            self._client = QdrantClient(location=":memory:")

    def create_collection(self, name: str, vector_size: int, distance_metric: str = "Cosine") -> None:
        metric = Distance.COSINE
        if distance_metric.lower() == "euclid":
            metric = Distance.EUCLID
        elif distance_metric.lower() == "dot":
            metric = Distance.DOT

        # Avoid raising error if exists
        existing = {c.name for c in self._client.get_collections().collections}
        if name in existing:
            return

        self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=metric)
        )

    def upsert_points(self, collection_name: str, points: List[VectorPoint]) -> int:
        structs = [
            PointStruct(id=p.id, vector=p.vector, payload=p.payload)
            for p in points
        ]
        self._client.upsert(collection_name=collection_name, points=structs)
        return len(structs)

    def search_points(
        self, 
        collection_name: str, 
        vector: List[float], 
        limit: int = 5, 
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        qdrant_filter = None
        if filters:
            conditions = []
            for k, v in filters.items():
                conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
            qdrant_filter = Filter(must=conditions)

        results = self._client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter
        )
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload
            }
            for r in results
        ]

    def delete_collection(self, name: str) -> bool:
        existing = {c.name for c in self._client.get_collections().collections}
        if name not in existing:
            return False
        self._client.delete_collection(collection_name=name)
        return True

    def count_points(self, collection_name: str) -> int:
        info = self._client.get_collection(collection_name=collection_name)
        return info.points_count or 0
