import time
from typing import Any, Dict
from langchain_core.messages import HumanMessage
from agents.base_agent import BaseAgent
from agents.schemas import AgentResponse
from agents.graph import compiled_graph
from shared.logging_config import get_logger

logger = get_logger(__name__)

class LangGraphAgent(BaseAgent):
    """An advanced autonomous agent powered by LangGraph with tool access."""

    def __init__(self) -> None:
        super().__init__(
            name="orchestrator",
            description="Autonomous LangGraph agent that can chain tools (Search -> Graph -> Summarize)."
        )

    async def run(
        self, 
        query: str, 
        conversation_id: str | None = None, 
        config: Dict[str, Any] | None = None
    ) -> AgentResponse:
        start_time = time.time()
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "conversation_id": conversation_id or "default",
            "steps": ["Initialized LangGraph agent"]
        }

        try:
            logger.info("agent.langgraph.invoke", query=query)
            
            # Pass thread_id for MemorySaver checkpointer
            graph_config = {"configurable": {"thread_id": initial_state["conversation_id"]}}
            
            final_state = await compiled_graph.ainvoke(initial_state, config=graph_config)
            
            last_message = final_state["messages"][-1]
            response_content = last_message.content if hasattr(last_message, "content") else str(last_message)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return AgentResponse(
                agent_name=self.name,
                status="completed",
                response=response_content,
                steps=final_state.get("steps", []),
                metadata={"elapsed_ms": elapsed_ms}
            )
        except Exception as e:
            logger.error("agent.langgraph.failed", error=str(e))
            elapsed_ms = (time.time() - start_time) * 1000
            return AgentResponse(
                agent_name=self.name,
                status="failed",
                response=f"Agent execution failed: {e}",
                steps=initial_state.get("steps", []),
                metadata={"elapsed_ms": elapsed_ms, "error": str(e)}
            )
