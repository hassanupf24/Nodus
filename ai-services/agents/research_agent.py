import time
from typing import Any, Dict
from agents.base_agent import BaseAgent
from agents.schemas import AgentResponse
from agents.tools import search_knowledge
from llm_runtime.service import get_llm_service
from llm_runtime.schemas import ChatRequest, ChatMessage, Role
from shared.logging_config import get_logger

logger = get_logger(__name__)

class ResearchAgent(BaseAgent):
    """Agent that performs semantic searches and synthesizes answers."""

    def __init__(self) -> None:
        super().__init__(
            name="research",
            description="Searches local indices and builds context to answer user prompts."
        )

    async def run(
        self, 
        query: str, 
        conversation_id: str | None = None, 
        config: Dict[str, Any] | None = None
    ) -> AgentResponse:
        start_time = time.time()
        steps = ["Analyzing query", "Searching local indices"]
        
        # 1. Search knowledge index
        limit = (config or {}).get("limit", 4)
        search_results = await search_knowledge(query, limit=limit)
        steps.append(f"Found {len(search_results)} relevant document chunks")

        # 2. Compile context
        context_str = ""
        for idx, r in enumerate(search_results):
            src = r.get("source") or "unknown source"
            context_str += f"\n--- Source {idx+1}: {src} ---\n{r.get('text', '')}\n"

        # 3. Call LLM
        system_prompt = (
            "You are the Nodus Research Agent. Your task is to answer the user's query "
            "strictly using the provided context chunks. If the context does not contain "
            "the answer, explain what you found but state that you do not have enough "
            "local information to answer completely. Do not invent facts."
        )

        user_content = f"Context Data:\n{context_str}\n\nQuery: {query}"
        
        try:
            llm = get_llm_service()
            req = ChatRequest(
                model=(config or {}).get("model", "llama3.2:3b"),
                messages=[ChatMessage(role=Role.USER, content=user_content)],
                system=system_prompt,
                stream=False
            )
            steps.append("Sending context to local LLM")
            resp = await llm.chat(req)
            answer = resp.message.content
            status = "completed"
        except Exception as e:
            logger.error("agent.research.llm_failed", error=str(e))
            steps.append(f"Local LLM call failed: {e}. Falling back to metadata summary.")
            
            # Fallback output
            answer = (
                "⚠️ Local LLM connection offline. Showing matched document references:\n\n"
            )
            for idx, r in enumerate(search_results):
                answer += f"- **Source {idx+1}:** {r.get('source')} (Score: {r.get('score'):.2f})\n"
                answer += f"  > *{r.get('text')[:200]}...*\n\n"
            status = "degraded"

        elapsed_ms = (time.time() - start_time) * 1000
        return AgentResponse(
            agent_name=self.name,
            status=status,
            response=answer,
            steps=steps,
            metadata={
                "elapsed_ms": elapsed_ms,
                "sources_used": [r.get("source") for r in search_results]
            }
        )
