"""FastAPI router for the search service."""

from __future__ import annotations

from fastapi import APIRouter, Query

from search.schemas import SearchRequest, SearchResponse, SuggestResponse
from search.service import get_search_service

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Execute a search query (vector, keyword, or hybrid)."""
    svc = get_search_service()
    return await svc.search(request)


@router.get("/suggest", response_model=SuggestResponse)
async def suggest(
    q: str = Query(..., min_length=1, description="Query prefix"),
    collection: str = Query("documents", description="Collection to search"),
    limit: int = Query(5, ge=1, le=20),
) -> SuggestResponse:
    """Get autocomplete suggestions for a query."""
    svc = get_search_service()
    suggestions = await svc.suggest(q, collection=collection, limit=limit)
    return SuggestResponse(suggestions=suggestions, query=q)
