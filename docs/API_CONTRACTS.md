# API Contracts

The Python backend exposes REST endpoints for state management and WebSocket endpoints for streaming agent interactions.

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Interaction (Streaming)

### `WS /chat/stream`
Establishes a bi-directional streaming connection with the LangGraph orchestrator.

**Client Message (JSON):**
```json
{
  "type": "user_input",
  "message": "Summarize the architectural differences between React and Svelte.",
  "context": {
    "active_window": "VSCode",
    "selected_files": ["app.tsx"]
  }
}
```

**Server Message (JSON - Token Stream):**
```json
{
  "type": "token",
  "content": "React"
}
```

**Server Message (JSON - Agent State Update):**
```json
{
  "type": "agent_state",
  "current_agent": "ResearchAgent",
  "status": "Searching local vector store for 'Svelte architecture'"
}
```

---

## 2. Ingestion

### `POST /ingest/file`
Upload a file for asynchronous processing (OCR, transcription, embedding).

**Request:** `multipart/form-data` (file)
**Response:**
```json
{
  "task_id": "uuid-1234",
  "status": "QUEUED"
}
```

### `GET /ingest/status/{task_id}`
**Response:**
```json
{
  "task_id": "uuid-1234",
  "status": "PROCESSING",
  "progress": 45,
  "message": "Generating embeddings..."
}
```

---

## 3. Memory & Graph API

### `GET /graph/entities`
Retrieve entities for visualization in the UI.

**Query Params:** `?type=Person&limit=100`

**Response:**
```json
{
  "entities": [
    {
      "id": "uuid-1",
      "name": "Alice",
      "type": "Person"
    }
  ]
}
```

### `GET /graph/neighbors/{entity_id}`
Retrieve connections for a specific node.

### `DELETE /memory/forget`
Instruct the system to unlearn a specific entity, document, or time range.
