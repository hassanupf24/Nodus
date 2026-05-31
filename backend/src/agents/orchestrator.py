import json
import operator
from collections.abc import AsyncGenerator, Sequence
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from models.llm import get_llm


class NodusState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    errors: list[str]


class AgentOrchestrator:
    def __init__(self) -> None:
        self.llm = get_llm()
        self.graph = self.build_graph()

    def build_graph(self) -> Any:
        """Builds the LangGraph state machine routing to specialized agents."""
        workflow = StateGraph(NodusState)

        async def system_agent_node(state: NodusState) -> dict[str, Any]:
            """The primary routing node. For now, it just responds to the user."""
            messages = state.get("messages", [])
            # Prepend system prompt
            system_prompt = SystemMessage(
                content="You are Nodus, a private cognitive AI. Be concise and helpful."
            )
            full_messages = [system_prompt] + list(messages)

            response = await self.llm.ainvoke(full_messages)
            return {"messages": [response], "current_agent": "SystemAgent"}

        workflow.add_node("system_agent", system_agent_node)
        workflow.add_edge(START, "system_agent")
        workflow.add_edge("system_agent", END)

        return workflow.compile()

    async def process_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Yields partial state updates for WebSockets."""
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "current_agent": "SystemAgent",
        }

        async for event in self.graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield json.dumps({"type": "token", "content": chunk.content})
            elif kind == "on_chain_end":
                if event["name"] == "system_agent":
                    yield json.dumps(
                        {
                            "type": "agent_state",
                            "current_agent": "SystemAgent",
                            "status": "Completed",
                        }
                    )
