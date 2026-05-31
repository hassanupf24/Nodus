# System Architecture

Nodus vNext is designed as a **Local-First Cognitive AI Operating System**, operating via a native Tauri desktop app communicating with a modular Python backend over local IPC and WebSockets. The system prioritizes local execution, multimodal memory, and multi-agent reasoning.

## High-Level Topology

```mermaid
graph TD
    subgraph "Desktop Shell (Tauri + Rust + React 19)"
        UI[React 19 Frontend]
        Zustand[State Management]
        IPC[Tauri IPC Bridge]
        
        UI <--> Zustand
        UI <--> IPC
    end

    subgraph "Cognitive Backend (FastAPI + Python 3.12+)"
        Gateway[FastAPI Gateway / WebSockets]
        Orchestrator[LangGraph Agent Orchestrator]
        MemEngine[Cognitive Memory Engine]
        Ingest[Multimodal Ingestion Pipeline]
        Security[Security & Vault Layer]
        
        Gateway <--> Orchestrator
        Gateway <--> Ingest
        Orchestrator <--> MemEngine
        Gateway <--> Security
    end

    subgraph "Data Persistence"
        VectorDB[(Qdrant Vector Store)]
        RelationalDB[(SQLite Metadata/Graph)]
        FS[Local Encrypted Filesystem]
        
        MemEngine <--> VectorDB
        MemEngine <--> RelationalDB
        Ingest <--> FS
        Ingest <--> VectorDB
        Ingest <--> RelationalDB
    end

    IPC <--> |REST & WebSockets| Gateway
```

## Core Components

### 1. Desktop Shell (Tauri v2)
The frontend is written in React 19 and Tailwind v4. It manages the presentation layer, command palette, and local file picking. Rust handles OS-level features (tray, native notifications, file system access).

### 2. Cognitive Backend (Python Monolith)
Built with FastAPI and organized into distinct domains:
- **Gateway**: Exposes REST and WebSocket endpoints.
- **Orchestrator**: LangGraph-based state machine routing user intent to specialized agents.
- **Memory Engine**: Manages Short-Term (session context), Episodic (historical events), Semantic (facts & entities), and Procedural (workflows) memory.
- **Retrieval**: Fuses vector (Qdrant), graph traversal (SQLite), and keyword search.
- **Ingestion**: Asynchronous task queue processing documents, images, and audio into the memory stores.
- **Security**: Local vault for credentials and encryption keys.

## Data Flow: Reasoning Loop

```mermaid
sequenceDiagram
    participant User
    participant ReactUI
    participant Gateway
    participant Orchestrator
    participant MemoryEngine
    participant Agents
    participant LLM

    User->>ReactUI: Ask complex question
    ReactUI->>Gateway: WebSocket /chat/stream
    Gateway->>Orchestrator: Dispatch request
    Orchestrator->>MemoryEngine: Retrieve context (Vector + Graph)
    MemoryEngine-->>Orchestrator: Augmented context
    Orchestrator->>Agents: Route to specific Agent (e.g., Research)
    Agents->>LLM: Generate multi-step reasoning plan
    LLM-->>Agents: Execute tools (Search, Synthesize)
    Agents-->>Orchestrator: Yield partial states
    Orchestrator-->>Gateway: Stream tokens
    Gateway-->>ReactUI: Render response
    Orchestrator->>MemoryEngine: Consolidate new memories
```

## Memory Architecture

The memory engine uses a layered approach inspired by human cognition.

```mermaid
graph TD
    Input[New Information] --> Parser[Semantic Parser]
    
    Parser --> STM[Short-Term Memory<br/>Session Buffer]
    Parser --> Episodic[Episodic Memory<br/>Time-series Events]
    
    STM --> Consolidation[Consolidation Engine]
    Episodic --> Consolidation
    
    Consolidation --> Semantic[Semantic Memory<br/>Entities & Knowledge Graph]
    Consolidation --> Procedural[Procedural Memory<br/>Rules & Workflows]
    
    subgraph Storage
        SQLite[(SQLite<br/>Graph & Metadata)]
        Qdrant[(Qdrant<br/>Embeddings)]
    end
    
    Semantic <--> SQLite
    Semantic <--> Qdrant
    Procedural <--> SQLite
```
