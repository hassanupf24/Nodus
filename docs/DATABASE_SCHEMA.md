# Database Schema

Nodus uses a dual-database architecture:
1. **SQLite**: Relational metadata, knowledge graph nodes/edges, episodic events, and application state.
2. **Qdrant (Embedded)**: Vector embeddings for semantic search.

## SQLite Schema (Knowledge Graph & Metadata)

```sql
-- Core Memory: Entities (Nodes)
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,           -- e.g., 'Person', 'Concept', 'Document'
    attributes JSON,              -- Flexible key-value pairs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core Memory: Relationships (Edges)
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,  -- e.g., 'AUTHORED', 'MENTIONS', 'IS_A'
    weight REAL DEFAULT 1.0,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_entity_id) REFERENCES entities(id),
    FOREIGN KEY(target_entity_id) REFERENCES entities(id)
);

-- Episodic Memory: Events
CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,     -- e.g., 'CONVERSATION', 'FILE_INGESTED'
    summary TEXT,
    context JSON
);

-- Documents & Sources
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'PENDING' -- PENDING, PROCESSING, COMPLETED, FAILED
);

-- Async Task Queue (Lightweight fallback)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    task_name TEXT NOT NULL,
    payload JSON,
    status TEXT DEFAULT 'QUEUED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Qdrant Schema (Vector Store)

Qdrant stores chunks of text with dense embeddings. Payload filtering allows hybrid search.

**Collection Name:** `nodus_memory`
**Vector Dimension:** Depends on model (e.g., 768 for nomic-embed-text)
**Distance Metric:** Cosine

**Payload Structure:**
```json
{
  "source_id": "uuid-of-document-or-episode",
  "chunk_index": 0,
  "text": "The actual text content...",
  "entity_ids": ["uuid-1", "uuid-2"], 
  "timestamp": 1715000000
}
```
