"""Pydantic schemas for the search service."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


class SearchRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.HYBRID
    collection: str = "documents"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    score_threshold: float | None = None
    filters: dict[str, Any] | None = None
    temporal_boost: bool = False
    recency_weight: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    source: str | None = None
    doc_id: str | None = None
    chunk_index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    highlights: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    results: list[SearchResult] = Field(default_factory=list)
    total: int = 0
    query: str = ""
    search_type: SearchType = SearchType.HYBRID
    elapsed_ms: float = 0.0


class SuggestResponse(BaseModel):
    suggestions: list[str] = Field(default_factory=list)
    query: str = ""
