"""Search service — hybrid vector + BM25 keyword + metadata filtering."""

from __future__ import annotations

import re
import time
import math
from typing import Any

from embedding.service import EmbeddingService, get_embedding_service
from search.query_analyzer import analyze_query
from search.ranking import reciprocal_rank_fusion, temporal_boost, recency_weighted_score
from search.schemas import SearchRequest, SearchResponse, SearchResult, SearchType
from shared.logging_config import get_logger
from shared.vector_store import QdrantManager, get_qdrant

logger = get_logger(__name__)


class SearchService:
    """Hybrid search combining vector similarity, BM25 keyword, and metadata filters."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        qdrant: QdrantManager | None = None,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
    ) -> None:
        self._embed = embedding_service or get_embedding_service()
        self._qdrant = qdrant or get_qdrant()
        self._bm25_weight = bm25_weight
        self._vector_weight = vector_weight

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Execute a search and return ranked results."""
        start = time.perf_counter()
        analyzed = analyze_query(request.query)

        # Merge inline filters from query with explicit filters
        all_filters = {**(request.filters or {}), **analyzed.filters_detected}

        results: list[SearchResult] = []

        if request.search_type == SearchType.VECTOR:
            results = await self._vector_search(
                request.query, request.collection, request.limit, request.score_threshold, all_filters
            )
        elif request.search_type == SearchType.KEYWORD:
            results = await self._keyword_search(
                analyzed.terms, request.collection, request.limit, all_filters
            )
        else:
            # Hybrid: run both and fuse
            vector_results = await self._vector_search(
                request.query, request.collection, request.limit * 2, request.score_threshold, all_filters
            )
            keyword_results = await self._keyword_search(
                analyzed.terms, request.collection, request.limit * 2, all_filters
            )
            results = self._fuse_results(vector_results, keyword_results, request.limit)

        # Apply recency weighting if requested
        if request.recency_weight > 0:
            for r in results:
                created = r.metadata.get("created_at", time.time())
                r.score = recency_weighted_score(r.score, float(created), weight=request.recency_weight)
            results.sort(key=lambda x: x.score, reverse=True)

        # Apply temporal boost
        if request.temporal_boost:
            result_dicts = [r.model_dump() for r in results]
            boosted = temporal_boost(result_dicts, timestamp_key="created_at")
            for i, rd in enumerate(boosted):
                if i < len(results):
                    results[i].score = rd.get("boosted_score", results[i].score)
            results.sort(key=lambda x: x.score, reverse=True)

        # Offset & limit
        total = len(results)
        results = results[request.offset: request.offset + request.limit]

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "search.completed",
            query=request.query,
            search_type=request.search_type.value,
            total=total,
            elapsed_ms=round(elapsed, 2),
        )

        return SearchResponse(
            results=results,
            total=total,
            query=request.query,
            search_type=request.search_type,
            elapsed_ms=round(elapsed, 2),
        )

    async def suggest(self, query: str, collection: str = "documents", limit: int = 5) -> list[str]:
        """Quick autocomplete-style suggestions based on existing documents."""
        results = await self._vector_search(query, collection, limit)
        seen: set[str] = set()
        suggestions: list[str] = []
        for r in results:
            # Use the first sentence as a suggestion
            first_sentence = r.text.split(".")[0].strip()
            if first_sentence and first_sentence not in seen:
                seen.add(first_sentence)
                suggestions.append(first_sentence[:100])
        return suggestions

    # ── Internal search methods ───────────────────────────

    async def _vector_search(
        self,
        query: str,
        collection: str,
        limit: int,
        score_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Pure vector similarity search."""
        vector = await self._embed.encode(query)
        raw = self._qdrant.search(
            collection=collection,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters,
        )
        return [
            SearchResult(
                id=r["id"],
                text=r["payload"].get("text", ""),
                score=r["score"],
                source=r["payload"].get("source"),
                doc_id=r["payload"].get("doc_id"),
                chunk_index=r["payload"].get("chunk_index"),
                metadata=r["payload"],
            )
            for r in raw
        ]

    async def _keyword_search(
        self,
        terms: list[str],
        collection: str,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """BM25-style keyword search using scroll + in-memory scoring.

        For production, this would be backed by an FTS index. Here we do a
        lightweight TF-IDF approximation over the Qdrant payloads.
        """
        if not terms:
            return []

        # Scroll all points (for small collections; production would use FTS)
        all_points = self._qdrant.client.scroll(
            collection_name=collection,
            limit=min(limit * 10, 1000),
            with_payload=True,
            with_vectors=False,
        )[0]

        scored: list[tuple[float, Any]] = []
        for point in all_points:
            text = (point.payload or {}).get("text", "").lower()
            # Simple TF scoring
            score = 0.0
            for term in terms:
                tf = text.count(term)
                if tf > 0:
                    score += 1 + math.log(1 + tf)
            if score > 0:
                # Check filters
                if filters:
                    payload = point.payload or {}
                    if not all(payload.get(k) == v for k, v in filters.items()):
                        continue
                scored.append((score, point))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            SearchResult(
                id=str(point.id),
                text=(point.payload or {}).get("text", ""),
                score=sc,
                source=(point.payload or {}).get("source"),
                doc_id=(point.payload or {}).get("doc_id"),
                chunk_index=(point.payload or {}).get("chunk_index"),
                metadata=point.payload or {},
                highlights=self._highlight(terms, (point.payload or {}).get("text", "")),
            )
            for sc, point in scored[:limit]
        ]

    def _fuse_results(
        self, vector_results: list[SearchResult], keyword_results: list[SearchResult], limit: int
    ) -> list[SearchResult]:
        """Merge vector and keyword results with RRF."""
        v_dicts = [r.model_dump() for r in vector_results]
        k_dicts = [r.model_dump() for r in keyword_results]
        merged = reciprocal_rank_fusion([v_dicts, k_dicts])
        results: list[SearchResult] = []
        for d in merged[:limit]:
            d.pop("rrf_score", None)
            results.append(SearchResult(**d))
        return results

    @staticmethod
    def _highlight(terms: list[str], text: str, context: int = 40) -> list[str]:
        """Extract snippets around matching terms."""
        highlights: list[str] = []
        lower = text.lower()
        for term in terms:
            idx = lower.find(term)
            if idx >= 0:
                start = max(0, idx - context)
                end = min(len(text), idx + len(term) + context)
                snippet = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")
                highlights.append(snippet)
        return highlights[:3]  # max 3 highlights


# ── Singleton ─────────────────────────────────────────────
_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    global _search_service  # noqa: PLW0603
    if _search_service is None:
        from shared.config import get_settings
        s = get_settings()
        _search_service = SearchService(bm25_weight=s.bm25_weight, vector_weight=s.vector_weight)
    return _search_service
