from typing import Annotated, Sequence, TypedDict, Any
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import time

from agents.tools import search_knowledge, store_graph_entity, store_graph_relationship, query_knowledge_graph
from shared.config import get_settings
from shared.logging_config import get_logger

logger = get_logger(__name__)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    conversation_id: str
    steps: Annotated[Sequence[str], operator.add]

@tool
async def search_memory(query: str, limit: int = 5) -> str:
    """Search the vector database for relevant memories and document chunks."""
    results = await search_knowledge(query, limit)
    if not results:
        return "No relevant information found."
    return "\n\n".join([f"Source: {r.get('source')}\nContent: {r.get('text')}" for r in results])

@tool
async def add_entity(name: str, entity_type: str, description: str = "") -> str:
    """Store a new entity in the knowledge graph."""
    res = await store_graph_entity(name, entity_type, description)
    return f"Entity {name} added. Result: {res}"

@tool
async def add_relationship(source_id: str, target_id: str, relation_type: str, weight: float = 1.0) -> str:
    """Store a relationship between two entities in the knowledge graph."""
    res = await store_graph_relationship(source_id, target_id, relation_type, weight)
    return f"Relationship added. Result: {res}"

@tool
async def query_graph(entity_name: str, max_depth: int = 2) -> str:
    """Query the knowledge graph for connections related to an entity."""
    res = await query_knowledge_graph(entity_name, max_depth)
    return str(res)

tools = [search_memory, add_entity, add_relationship, query_graph]
tool_node = ToolNode(tools)

def get_llm():
    settings = get_settings()
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model="llama3.2:3b",  # Can be overridden by config
        temperature=0.0
    ).bind_tools(tools)

async def call_model(state: AgentState):
    logger.info("agent.graph.call_model", messages_count=len(state["messages"]))
    llm = get_llm()
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response], "steps": ["Called LLM model"]}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

from langgraph.checkpoint.memory import MemorySaver

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    }
)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
compiled_graph = workflow.compile(checkpointer=memory)
