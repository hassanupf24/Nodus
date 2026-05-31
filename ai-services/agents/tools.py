import os
from typing import Any, Dict, List, Optional
from search.service import get_search_service
from search.schemas import SearchRequest, SearchType
from knowledge_graph.service import get_graph_service
from knowledge_graph.schemas import Entity, Relationship, GraphQuery
from shared.logging_config import get_logger

logger = get_logger(__name__)

async def search_knowledge(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search the vector database and return relevant document chunks."""
    try:
        search_svc = get_search_service()
        req = SearchRequest(query=query, limit=limit, search_type=SearchType.HYBRID)
        resp = await search_svc.search(req)
        return [
            {
                "id": r.id,
                "text": r.text,
                "score": r.score,
                "source": r.source,
                "metadata": r.metadata
            }
            for r in resp.results
        ]
    except Exception as e:
        logger.error("agent.tool.search_knowledge_failed", error=str(e))
        return []

async def store_graph_entity(name: str, entity_type: str, description: Optional[str] = None) -> str:
    """Store an entity vertex in the local knowledge graph."""
    try:
        graph_svc = await get_graph_service()
        ent = Entity(name=name, entity_type=entity_type, description=description or "")
        return await graph_svc.add_entity(ent)
    except Exception as e:
        logger.error("agent.tool.store_entity_failed", error=str(e))
        return f"Error: {e}"

async def store_graph_relationship(source_id: str, target_id: str, relation_type: str, weight: float = 1.0) -> str:
    """Store a semantic relationship edge between two entities in the knowledge graph."""
    try:
        graph_svc = await get_graph_service()
        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight
        )
        return await graph_svc.add_relationship(rel)
    except Exception as e:
        logger.error("agent.tool.store_relationship_failed", error=str(e))
        return f"Error: {e}"

async def query_knowledge_graph(entity_name: str, max_depth: int = 2) -> Dict[str, Any]:
    """Retrieve connected neighbors of an entity from the knowledge graph."""
    try:
        graph_svc = await get_graph_service()
        q = GraphQuery(entity_name=entity_name, max_depth=max_depth)
        resp = await graph_svc.query_graph(q)
        return resp.model_dump()
    except Exception as e:
        logger.error("agent.tool.query_graph_failed", error=str(e))
        return {"nodes": [], "edges": []}
