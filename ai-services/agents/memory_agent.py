import time
from typing import Any, Dict
from agents.base_agent import BaseAgent
from agents.schemas import AgentResponse
from agents.tools import query_knowledge_graph, store_graph_entity, store_graph_relationship
from knowledge_graph.service import get_graph_service
from knowledge_graph.schemas import ExtractionRequest
from shared.logging_config import get_logger

logger = get_logger(__name__)

class MemoryAgent(BaseAgent):
    """Agent that manages entity memories and extracts graph elements from sessions."""

    def __init__(self) -> None:
        super().__init__(
            name="memory",
            description="Manages personal memory graph, extracts facts and binds relationship links."
        )

    async def run(
        self, 
        query: str, 
        conversation_id: str | None = None, 
        config: Dict[str, Any] | None = None
    ) -> AgentResponse:
        start_time = time.time()
        steps = ["Parsing conversation text", "Checking knowledge graph"]
        
        # 1. Extract entities & relationships using local LLM extractor
        extracted_entities = []
        extracted_relations = []
        try:
            graph_svc = await get_graph_service()
            steps.append("Invoking graph extractor pipeline")
            req = ExtractionRequest(
                text=query,
                source=f"chat-{conversation_id}" if conversation_id else "chat-session",
                extract_relationships=True
            )
            resp = await graph_svc.extract_and_store(req)
            extracted_entities = [e.name for e in resp.entities]
            extracted_relations = [f"{r.source_id} -> {r.relation_type} -> {r.target_id}" for r in resp.relationships]
            steps.append(f"Stored {len(extracted_entities)} entities & {len(extracted_relations)} edges")
        except Exception as e:
            logger.error("agent.memory.extraction_failed", error=str(e))
            steps.append(f"Failed to auto-extract graph elements: {e}")

        # 2. Check query for specific entities and return related nodes
        steps.append("Scanning query for existing graph memories")
        retrieved_memories = []
        # Simple string-match heuristic for query entities
        try:
            graph_svc = await get_graph_service()
            all_nodes = await graph_svc.find_entities(limit=100)
            for node in all_nodes:
                if node.name.lower() in query.lower():
                    neighbors = await query_knowledge_graph(node.name)
                    retrieved_memories.append({
                        "entity": node.name,
                        "type": node.entity_type,
                        "description": node.description,
                        "connections": len(neighbors.get("edges", []))
                    })
        except Exception as e:
            logger.error("agent.memory.retrieval_failed", error=str(e))

        # 3. Construct response
        response_text = ""
        if extracted_entities or extracted_relations:
            response_text += "### 🧠 Memory Persisted\n"
            if extracted_entities:
                response_text += f"- **Entities Extracted:** {', '.join(extracted_entities)}\n"
            if extracted_relations:
                response_text += "- **Relationships Mapped:**\n"
                for rel in extracted_relations:
                    response_text += f"  - `{rel}`\n"
            response_text += "\n"

        if retrieved_memories:
            response_text += "### 🔍 Related Graph Nodes Found\n"
            for mem in retrieved_memories:
                response_text += f"- **{mem['entity']}** ({mem['type']}): {mem['description']} (*Connected to {mem['connections']} other concept(s)*)\n"
        else:
            if not (extracted_entities or extracted_relations):
                response_text = "No immediate entities or relationships were extracted or matched from the query."

        elapsed_ms = (time.time() - start_time) * 1000
        return AgentResponse(
            agent_name=self.name,
            status="completed",
            response=response_text,
            steps=steps,
            metadata={
                "elapsed_ms": elapsed_ms,
                "extracted_entities": extracted_entities,
                "extracted_relations": extracted_relations
            }
        )
