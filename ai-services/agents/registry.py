from typing import Dict, List
from agents.base_agent import BaseAgent
from agents.research_agent import ResearchAgent
from agents.memory_agent import MemoryAgent
from agents.summarizer_agent import SummarizerAgent
from agents.langgraph_agent import LangGraphAgent
from shared.logging_config import get_logger

logger = get_logger(__name__)

class AgentRegistry:
    """Registry maintaining references to all available Nodus AI Agents."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        # Auto-register core agents
        self.register(ResearchAgent())
        self.register(MemoryAgent())
        self.register(SummarizerAgent())
        self.register(LangGraphAgent())

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent
        logger.info("agent.registered", name=agent.name)

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> List[Dict[str, str]]:
        return [
            {"name": agent.name, "description": agent.description}
            for agent in self._agents.values()
        ]

# Singleton instance
_registry = AgentRegistry()

def get_agent_registry() -> AgentRegistry:
    return _registry
