"""Route registration — mounts every sub-service router on the gateway."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI

from shared.logging_config import get_logger

logger = get_logger(__name__)


def register_routes(app: FastAPI) -> None:
    """Import and mount all sub-service routers under their prefixes."""

    # ── LLM runtime ──────────────────────────────────────
    from llm_runtime.router import router as llm_router

    app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM Runtime"])

    # ── Embedding ────────────────────────────────────────
    from embedding.router import router as embed_router

    app.include_router(embed_router, prefix="/api/v1/embeddings", tags=["Embeddings"])

    # ── Search ───────────────────────────────────────────
    from search.router import router as search_router

    app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])

    # ── Knowledge Graph ──────────────────────────────────
    from knowledge_graph.router import router as kg_router

    app.include_router(kg_router, prefix="/api/v1/graph", tags=["Knowledge Graph"])

    # ── Agents ───────────────────────────────────────────
    from agents.router import router as agents_router

    app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])

    # ── Ingestion ────────────────────────────────────────
    from ingestion_services.router import router as ingestion_router

    app.include_router(ingestion_router, prefix="/api/v1", tags=["Ingestion Pipeline"])

    # ── Vector ───────────────────────────────────────────
    from vector_services.router import router as vector_router

    app.include_router(vector_router, prefix="/api/v1", tags=["Vector Operations"])

    logger.info("gateway.routes_registered")
