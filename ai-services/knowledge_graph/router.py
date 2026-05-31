"""FastAPI router for the knowledge graph."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from knowledge_graph.schemas import (
    Entity,
    ExtractionRequest,
    ExtractionResponse,
    GraphQuery,
    GraphResponse,
    Relationship,
)
from knowledge_graph.service import get_graph_service

router = APIRouter()


# ── Entities ──────────────────────────────────────────────


@router.post("/entities", response_model=dict)
async def create_entity(entity: Entity) -> dict[str, str]:
    svc = await get_graph_service()
    eid = await svc.add_entity(entity)
    return {"id": eid}


@router.get("/entities/{entity_id}", response_model=Entity)
async def get_entity(entity_id: str) -> Entity:
    svc = await get_graph_service()
    entity = await svc.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/entities", response_model=list[Entity])
async def list_entities(
    name: str | None = None,
    entity_type: str | None = None,
    limit: int = 50,
) -> list[Entity]:
    svc = await get_graph_service()
    return await svc.find_entities(name=name, entity_type=entity_type, limit=limit)


@router.get("/entities/search/{query}", response_model=list[Entity])
async def search_entities(query: str, limit: int = 20) -> list[Entity]:
    svc = await get_graph_service()
    return await svc.search_entities(query, limit=limit)


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str) -> dict[str, Any]:
    svc = await get_graph_service()
    deleted = await svc.delete_entity(entity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"deleted": True, "id": entity_id}


# ── Relationships ─────────────────────────────────────────


@router.post("/relationships", response_model=dict)
async def create_relationship(rel: Relationship) -> dict[str, str]:
    svc = await get_graph_service()
    rid = await svc.add_relationship(rel)
    return {"id": rid}


@router.get("/relationships/{entity_id}", response_model=list[Relationship])
async def get_relationships(entity_id: str, relation_type: str | None = None) -> list[Relationship]:
    svc = await get_graph_service()
    return await svc.get_relationships(entity_id, relation_type=relation_type)


@router.delete("/relationships/{rel_id}")
async def delete_relationship(rel_id: str) -> dict[str, Any]:
    svc = await get_graph_service()
    deleted = await svc.delete_relationship(rel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return {"deleted": True, "id": rel_id}


# ── Graph queries ─────────────────────────────────────────


@router.post("/query", response_model=GraphResponse)
async def query_graph(query: GraphQuery) -> GraphResponse:
    svc = await get_graph_service()
    return await svc.query_graph(query)


@router.get("/path")
async def find_path(from_id: str, to_id: str, max_depth: int = 5) -> dict[str, Any]:
    svc = await get_graph_service()
    path = await svc.find_path(from_id, to_id, max_depth=max_depth)
    if path is None:
        raise HTTPException(status_code=404, detail="No path found")
    return {"path": path, "length": len(path) - 1}


# ── Extraction ────────────────────────────────────────────


@router.post("/extract", response_model=ExtractionResponse)
async def extract_entities(request: ExtractionRequest) -> ExtractionResponse:
    svc = await get_graph_service()
    return await svc.extract_and_store(request)


@router.get("/stats")
async def graph_stats() -> dict[str, int]:
    svc = await get_graph_service()
    return await svc.stats()
