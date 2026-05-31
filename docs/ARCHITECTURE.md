# Nodus System Architecture

This document describes the high-level architecture, design patterns, data flows, and database schemas of the Nodus local-first AI memory platform.

---

## 1. High-Level Architecture Overview

Nodus is structured as an offline-first desktop application with a decoupled, polyglot backend microservice layer. The local architecture ensures user data never leaves the host machine unless E2E encrypted synchronization is explicitly enabled.

```mermaid
graph TD
    subgraph UI ["Desktop Application (Tauri + React)"]
        App["App Shell / Router"]
        Chat["Chat Interface"]
        Graph["React Flow Graph"]
        Search["Search Panel"]
        Store["Zustand State Store"]
    end

    subgraph Core ["Tauri Rust Core"]
        Cmds["Rust API Commands"]
        DBReplica["SQLite Crypt (SQLCipher)"]
        FsMonitor["FS Watcher (Notify)"]
    end

    subgraph Backend ["Local Python AI Services"]
        Gw["FastAPI Gateway (Port 8000)"]
        LLM["Ollama / llama.cpp"]
        Embed["Sentence-Transformers"]
        SearchSvc["Hybrid Search Engine"]
        GraphSvc["SQLite Knowledge Graph"]
        AgentOrch["Multi-Agent Orchestrator"]
        Ingest["Ingestion Pipeline"]
        Vector["Qdrant Vector DB"]
    end

    App --> Store
    Chat --> Cmds
    Search --> Cmds
    Graph --> Cmds
    
    Cmds --> Gw
    Gw --> LLM
    Gw --> Embed
    Gw --> SearchSvc
    Gw --> GraphSvc
    Gw --> AgentOrch
    Gw --> Ingest
    
    Ingest --> Embed
    Ingest --> Vector
    Ingest --> GraphSvc
    SearchSvc --> Vector
    SearchSvc --> GraphSvc
```

### Technology Rationale
*   **Tauri v2 + React 19:** Combines the security and memory safety of Rust with a fast, modern HTML/JS rendering interface. Tauri uses the system webview to reduce the memory footprint relative to Electron.
*   **FastAPI:** High performance, asynchronous Python web framework used for rapid model execution and integration with AI frameworks (ONNX, Sentence-Transformers, LangGraph).
*   **Qdrant Embedded:** Lightweight, high-speed vector index running entirely in-process to avoid the management overhead of an external daemon.
*   **SQLite (SQLCipher):** Secure, relational database that manages the personal knowledge graph, text metadata, and audit logs.

---

## 2. Ingestion & Embedding Pipeline

The event-driven ingestion pipeline processes files from the local filesystem, extracts raw text, generates semantic vectors, and creates nodes in the knowledge graph.

```mermaid
sequenceDiagram
    participant User
    participant App as React App
    participant Gw as API Gateway
    participant Pipe as Ingestion Pipeline
    participant Ch as Semantic Chunker
    participant Emb as Embedding Service
    participant Vec as Qdrant DB
    participant Graph as Graph Store

    User->>App: Drag & drop document
    App->>Gw: POST /api/v1/ingest (file_path)
    Gw->>Pipe: Run Ingestion Job
    Pipe->>Pipe: Parse file (PDF/DOCX/HTML)
    Pipe->>Ch: Split text into chunks (size=1000, overlap=200)
    Ch-->>Pipe: Return text fragments
    loop For each chunk
        Pipe->>Emb: POST /embeddings (text)
        Emb-->>Pipe: Dense vector (384-dim)
        Pipe->>Vec: Upsert Point (ID, Vector, Payload)
    end
    Pipe->>Graph: Extract and store entities (spaCy/LLM)
    Graph-->>Pipe: Save vertices & edges
    Pipe-->>Gw: Job completed
    Gw-->>App: Broadcast Ingestion Status (Zustand)
```

---

## 3. Hybrid Search Retrieval

Nodus implements reciprocal rank fusion (RRF) to combine dense vector search with sparse keyword indexing.

```mermaid
graph TD
    Query["User Query"] --> Analyzer["Query Intent Analyzer"]
    Analyzer --> Vector["Vector Search (Cosine similarity)"]
    Analyzer --> BM25["Sparse Keyword Search (BM25)"]
    
    Vector --> RRF["Reciprocal Rank Fusion (RRF)"]
    BM25 --> RRF
    
    RRF --> Temporal["Temporal Boost (Recency weighting)"]
    Temporal --> Final["Ranked Search Results"]
```

*   **RRF Fusion Formula:**
    $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
    Where $r_m(d)$ is the rank of document $d$ in retrieval method $m$, and $k$ is a constant (typically 60) to prevent outlier results from dominating.

---

## 4. Database Architecture & Schema

### SQLite Knowledge Graph Schema
The structural knowledge graph and timeline metrics are persisted in local SQLite. Key tables are structured as follows:

```mermaid
erDiagram
    entities {
        text id PK
        text name
        text entity_type
        text description
        integer created_at
    }
    relationships {
        text id PK
        text source_id FK
        text target_id FK
        text relation_type
        real weight
        integer created_at
    }
    timeline_events {
        text id PK
        text title
        text description
        integer timestamp
        text event_type
        text source
    }
    
    entities ||--o{ relationships : "source_id / target_id"
    timeline_events }o--o{ entities : "references"
```

---

## 5. Security & Key Management

Nodus uses a zero-knowledge local execution profile:
1.  **Encryption at Rest:** All SQLite instances are initialized with **SQLCipher** using AES-256-CBC encryption.
2.  **OS Keychain Integration:** Database keys and sync credentials are encrypted and stored in the native OS credential store (Windows Credential Manager / macOS Keychain / Linux Secret Service) using Tauri's secure storage bindings.
3.  **Local Inference Sandboxing:** The local LLM and embedding runtimes execute entirely in localhost loops. Network ports are bound to `127.0.0.1` by default to prevent external access.
