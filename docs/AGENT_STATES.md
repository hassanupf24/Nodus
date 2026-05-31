# Agent States & Workflows

Nodus uses **LangGraph** to model agents as deterministic, durable state machines. This ensures multi-step reasoning is robust, observable, and supports human-in-the-loop interventions.

## State Schema

The core state passed between agents is defined as follows:

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class NodusState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    active_memory_context: dict
    entities_extracted: list[dict]
    task_plan: list[str]
    errors: list[str]
```

## System Orchestrator Workflow

The `SystemAgent` acts as the router and orchestrator.

```mermaid
stateDiagram-v2
    [*] --> SystemAgent
    
    state SystemAgent {
        ParseIntent
        RetrieveContext
        Route
    }
    
    SystemAgent --> ResearchAgent : Needs deep search
    SystemAgent --> WriterAgent : Needs drafting
    SystemAgent --> CodingAgent : Code-related task
    SystemAgent --> MemoryAgent : Consolidate facts
    
    ResearchAgent --> SystemAgent : Return findings
    WriterAgent --> SystemAgent : Return draft
    CodingAgent --> SystemAgent : Return code
    MemoryAgent --> SystemAgent : Memory saved
    
    SystemAgent --> FormulateResponse
    FormulateResponse --> [*]
```

## Research Agent Flow

The Research Agent executes a guarded reasoning loop to explore local and external data.

```mermaid
stateDiagram-v2
    [*] --> DecomposeQuery
    DecomposeQuery --> RetrieveVector
    DecomposeQuery --> TraverseGraph
    
    RetrieveVector --> Synthesize
    TraverseGraph --> Synthesize
    
    Synthesize --> EvaluateAdequacy
    EvaluateAdequacy --> DecomposeQuery : Insufficient Info
    EvaluateAdequacy --> [*] : Sufficient Info
```

## Planner Agent Flow

Used for complex workflows spanning multiple sessions.

```mermaid
stateDiagram-v2
    [*] --> AnalyzeRequest
    AnalyzeRequest --> GenerateSubtasks
    GenerateSubtasks --> ExecuteSubtask
    ExecuteSubtask --> ValidateSubtask
    ValidateSubtask --> ExecuteSubtask : Next subtask
    ValidateSubtask --> [*] : All complete
```
