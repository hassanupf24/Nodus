from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from agents.schemas import AgentRequest, AgentResponse
from agents.orchestrator import AgentOrchestrator, get_agent_orchestrator
from agents.registry import get_agent_registry, AgentRegistry

router = APIRouter(tags=["Agents"])

@router.post("/invoke", response_model=AgentResponse)
async def invoke_agent(
    request: AgentRequest,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
) -> AgentResponse:
    """Invoke a registered agent by name to run a specific task or query."""
    response = await orchestrator.execute(request)
    if response.status == "failed":
        raise HTTPException(status_code=500, detail=response.response)
    return response

@router.get("", response_model=List[Dict[str, str]])
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry)
) -> List[Dict[str, str]]:
    """Get a list of all registered agents and their capabilities."""
    return registry.list_agents()
