# Nodus API Reference

This document describes the REST API surface exposed by the Nodus local services layer on `http://localhost:8000`.

---

## 1. Health API

### `GET /health`
Get the general health status of the Nodus microservices and model engines.

**Response (JSON):**
```json
{
  "uptime_seconds": 124.5,
  "services": [
    {
      "name": "ollama",
      "status": "healthy",
      "latency_ms": 12.4
    }
  ]
}
```

---

## 2. LLM Runtime API

### `POST /api/v1/llm/chat`
Execute a prompt query against the active LLM. Supports standard completion and SSE token streaming.

**Request Headers:**
*   `Content-Type: application/json`

**Request Body:**
```json
{
  "model": "llama3.2:3b",
  "messages": [
    {
      "role": "user",
      "content": "What is the core principle of Nodus?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2048,
  "stream": false
}
```

**Response (JSON - `stream: false`):**
```json
{
  "model": "llama3.2:3b",
  "message": {
    "role": "assistant",
    "content": "The core principle of Nodus is local-first privacy. It runs LLM inference and stores knowledge indices entirely on-device."
  },
  "done": true,
  "total_duration": 1450201004,
  "eval_count": 28,
  "eval_duration": 820102000,
  "tokens_per_second": 34.1
}
```

**Response (SSE - `stream: true`):**
A sequence of Server-Sent Events containing JSON fragments.
```
event: message
data: {"model":"llama3.2:3b","content":"The","done":false}

event: message
data: {"model":"llama3.2:3b","content":" core","done":false}

event: message
data: {"model":"llama3.2:3b","content":"","done":true}
```

---

## 3. Embedding API

### `POST /api/v1/embeddings`
Generate a dense float array representation for text fragments.

**Request Body:**
```json
{
  "model": "nomic-embed-text",
  "input": "Nodus is an offline-first private memory application."
}
```

**Response (JSON):**
```json
{
  "model": "nomic-embed-text",
  "embeddings": [
    [0.0124, -0.0452, 0.1082, "... (384 dimensions)"]
  ]
}
```

---

## 4. Search API

### `POST /api/v1/search`
Perform a hybrid (vector similarity + BM25 keyword) search query across the local database indices.

**Request Body:**
```json
{
  "query": "local encryption keys",
  "limit": 5,
  "search_type": "hybrid",
  "filters": {
    "file_type": "pdf"
  }
}
```

**Response (JSON):**
```json
{
  "query": "local encryption keys",
  "search_type": "hybrid",
  "elapsed_ms": 14.5,
  "total": 1,
  "results": [
    {
      "id": "chunk-uuid-1024",
      "text": "All Nodus SQLite files are encrypted on the host machine using SQLCipher keys.",
      "score": 0.892,
      "source": "D:/Documents/Security.pdf",
      "metadata": {
        "created_at": 1716738902.0
      }
    }
  ]
}
```

---

## 5. Ingestion API

### `POST /api/v1/ingest`
Schedule a background task to process a local file path into vector chunks and knowledge graph relationships.

**Request Body:**
```json
{
  "file_path": "D:/Documents/Research/RAG-spec.pdf",
  "collection_name": "documents"
}
```

**Response (JSON):**
```json
{
  "job_id": "job-uuid-8893",
  "status": "processing"
}
```

---

## 6. Knowledge Graph API

### `GET /api/v1/graph/stats`
Get nodes and relationships counts.

**Response (JSON):**
```json
{
  "nodes": 142,
  "relationships": 893
}
```

### `POST /api/v1/graph/query`
Query connected neighbors of a given node depth-wise.

**Request Body:**
```json
{
  "entity_name": "Qdrant",
  "max_depth": 2,
  "limit": 10
}
```

**Response (JSON):**
```json
{
  "nodes": [
    {
      "id": "node-1",
      "name": "Qdrant",
      "entity_type": "organization",
      "description": "Vector database engine."
    },
    {
      "id": "node-2",
      "name": "Nodus",
      "entity_type": "project",
      "description": "Local-first AI platform."
    }
  ],
  "edges": [
    {
      "source": "node-2",
      "target": "node-1",
      "relation_type": "uses",
      "weight": 1.0
    }
  ]
}
```

---

## 7. Agents API

### `POST /api/v1/agents/invoke`
Trigger a registered specialized agent to complete a task.

**Request Body:**
```json
{
  "agent_name": "summarizer",
  "query": "Long document text to compress..."
}
```

**Response (JSON):**
```json
{
  "agent_name": "summarizer",
  "status": "completed",
  "response": "# Summary\nCore subject details...",
  "steps": [
    "Analyzing input text",
    "Sending text chunks to local LLM"
  ],
  "metadata": {
    "elapsed_ms": 420.5
  }
}
```
