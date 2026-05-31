"""Pydantic schemas for the knowledge graph."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    CONCEPT = "concept"
    TOPIC = "topic"
    DOCUMENT = "document"
    LOCATION = "location"
    EVENT = "event"
    TECHNOLOGY = "technology"
    OTHER = "other"


class Entity(BaseModel):
    id: str | None = None
    name: str
    entity_type: EntityType = EntityType.CONCEPT
    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Relationship(BaseModel):
    id: str | None = None
    source_id: str
    target_id: str
    relation_type: str  # e.g. "mentions", "related_to", "authored_by"
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GraphQuery(BaseModel):
    """A query against the knowledge graph."""

    entity_id: str | None = None
    entity_name: str | None = None
    relation_type: str | None = None
    max_depth: int = Field(default=2, ge=1, le=5)
    limit: int = Field(default=50, ge=1, le=500)


class GraphNode(BaseModel):
    id: str
    name: str
    entity_type: str
    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str
    weight: float = 1.0


class GraphResponse(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0


class ExtractionRequest(BaseModel):
    text: str
    source: str | None = None
    extract_relationships: bool = True


class ExtractionResponse(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
