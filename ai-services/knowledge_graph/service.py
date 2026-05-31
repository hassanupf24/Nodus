"""Knowledge graph service — high-level API over the graph store and extractor."""

from __future__ import annotations

from typing import Any

from knowledge_graph.extractor import EntityExtractor
from knowledge_graph.schemas import (
    Entity,
    ExtractionRequest,
    ExtractionResponse,
    GraphQuery,
    GraphResponse,
    GraphEdge,
    GraphNode,
    Relationship,
)
from knowledge_graph.store import GraphStore, get_graph_store
from shared.logging_config import get_logger

logger = get_logger(__name__)


class GraphService:
    """High-level knowledge-graph service."""

    def __init__(self, store: GraphStore | None = None) -> None:
        self._store = store
        self._extractor = EntityExtractor()

    async def _get_store(self) -> GraphStore:
        if self._store is None:
            self._store = await get_graph_store()
        return self._store

    # ── Entity CRUD ───────────────────────────────────────

    async def add_entity(self, entity: Entity) -> str:
        store = await self._get_store()
        return await store.add_entity(entity)

    async def get_entity(self, entity_id: str) -> Entity | None:
        store = await self._get_store()
        return await store.get_entity(entity_id)

    async def find_entities(
        self, name: str | None = None, entity_type: str | None = None, limit: int = 50
    ) -> list[Entity]:
        store = await self._get_store()
        return await store.find_entities(name=name, entity_type=entity_type, limit=limit)

    async def search_entities(self, query: str, limit: int = 20) -> list[Entity]:
        store = await self._get_store()
        return await store.search_entities(query, limit=limit)

    async def delete_entity(self, entity_id: str) -> bool:
        store = await self._get_store()
        return await store.delete_entity(entity_id)

    # ── Relationship CRUD ─────────────────────────────────

    async def add_relationship(self, rel: Relationship) -> str:
        store = await self._get_store()
        return await store.add_relationship(rel)

    async def get_relationships(self, entity_id: str, relation_type: str | None = None) -> list[Relationship]:
        store = await self._get_store()
        return await store.get_relationships(entity_id, relation_type=relation_type)

    async def delete_relationship(self, rel_id: str) -> bool:
        store = await self._get_store()
        return await store.delete_relationship(rel_id)

    # ── Graph queries ─────────────────────────────────────

    async def query_graph(self, query: GraphQuery) -> GraphResponse:
        store = await self._get_store()

        entity_id = query.entity_id
        if not entity_id and query.entity_name:
            results = await store.find_entities(name=query.entity_name, limit=1)
            if results:
                entity_id = results[0].id

        if not entity_id:
            return GraphResponse()

        data = await store.get_neighbors(entity_id, max_depth=query.max_depth, limit=query.limit)
        nodes = [
            GraphNode(
                id=n["id"],
                name=n["name"],
                entity_type=n["entity_type"],
                description=n.get("description"),
            )
            for n in data["nodes"]
        ]
        edges = [
            GraphEdge(
                source=e["source"],
                target=e["target"],
                relation_type=e["relation_type"],
                weight=e.get("weight", 1.0),
            )
            for e in data["edges"]
        ]
        return GraphResponse(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
        )

    async def find_path(self, from_id: str, to_id: str, max_depth: int = 5) -> list[str] | None:
        store = await self._get_store()
        return await store.find_path(from_id, to_id, max_depth=max_depth)

    # ── Extraction ────────────────────────────────────────

    async def extract_and_store(self, request: ExtractionRequest) -> ExtractionResponse:
        """Extract entities/relationships from text and store in the graph."""
        result = await self._extractor.extract(request.text, source=request.source)
        store = await self._get_store()

        stored_entities: list[Entity] = []
        entity_name_to_id: dict[str, str] = {}

        for entity in result["entities"]:
            eid = await store.add_entity(entity)
            entity.id = eid
            stored_entities.append(entity)
            entity_name_to_id[entity.name.lower()] = eid

        stored_rels: list[Relationship] = []
        if request.extract_relationships:
            for rel in result["relationships"]:
                # Map names to stored IDs
                src_id = entity_name_to_id.get(rel.source_id.lower(), rel.source_id)
                tgt_id = entity_name_to_id.get(rel.target_id.lower(), rel.target_id)
                rel.source_id = src_id
                rel.target_id = tgt_id
                try:
                    rid = await store.add_relationship(rel)
                    rel.id = rid
                    stored_rels.append(rel)
                except Exception as exc:
                    logger.warning("graph.rel_store_failed", error=str(exc))

        return ExtractionResponse(entities=stored_entities, relationships=stored_rels)

    async def stats(self) -> dict[str, int]:
        store = await self._get_store()
        return await store.stats()


# ── Singleton ─────────────────────────────────────────────
_graph_service: GraphService | None = None


async def get_graph_service() -> GraphService:
    global _graph_service  # noqa: PLW0603
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
