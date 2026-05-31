import time
from typing import Any, Dict, List
from agents.registry import get_agent_registry
from agents.schemas import AgentRequest, AgentResponse
from shared.logging_config import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """Orchestrates agent selection and coordinates multi-agent workflows."""

    def __init__(self) -> None:
        self.registry = get_agent_registry()

    async def execute(self, request: AgentRequest) -> AgentResponse:
        start_time = time.time()
        agent = self.registry.get(request.agent_name)
        
        if not agent:
            logger.error("agent.orchestrator.agent_not_found", name=request.agent_name)
            return AgentResponse(
                agent_name=request.agent_name,
                status="failed",
                response=f"Agent '{request.agent_name}' was not found in registry.",
                steps=["Validating agent name"],
                metadata={"error": "Agent not found"}
            )

        logger.info("agent.orchestrator.executing", agent=request.agent_name, query_len=len(request.query))
        
        try:
            response = await agent.run(
                query=request.query,
                conversation_id=request.conversation_id,
                config=request.config
            )
            return response
        except Exception as e:
            logger.error("agent.orchestrator.execution_failed", agent=request.agent_name, error=str(e))
            return AgentResponse(
                agent_name=request.agent_name,
                status="failed",
                response=f"Execution of agent '{request.agent_name}' failed with error: {e}",
                steps=["Validating agent name", "Executing agent run"],
                metadata={"error": str(e)}
            )

_orchestrator = AgentOrchestrator()

def get_agent_orchestrator() -> AgentOrchestrator:
    return _orchestrator
