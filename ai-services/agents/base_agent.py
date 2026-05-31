from abc import ABC, abstractmethod
from typing import Any, Dict, List
from agents.schemas import AgentResponse

class BaseAgent(ABC):
    """Abstract base class representing a Nodus AI Agent."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.tools: List[Any] = []

    @abstractmethod
    async def run(
        self, 
        query: str, 
        conversation_id: str | None = None, 
        config: Dict[str, Any] | None = None
    ) -> AgentResponse:
        """Run the agent against the user query."""
        pass
