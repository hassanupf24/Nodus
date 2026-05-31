from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class NodusState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    errors: list[str]

class AgentOrchestrator:
    def __init__(self) -> None:
        pass
        
    def build_graph(self) -> None:
        """Builds the LangGraph state machine routing to specialized agents."""
        pass
        
    async def process_stream(self, state: NodusState):
        """Yields partial state updates for WebSockets."""
        yield {"status": "Processing"}
