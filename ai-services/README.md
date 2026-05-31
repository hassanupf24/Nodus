# Nodus AI Services

**Local-First Private AI Memory Infrastructure — Backend Microservices**

## Architecture

Nodus AI Services is a modular Python backend that powers the Nodus desktop application.
Every service runs **locally** on the user's machine — no cloud dependencies, no data leaves
the device.

```
┌──────────────────────────────────────────────────┐
│                   Tauri Desktop App              │
│                  (localhost HTTP)                 │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│               API Gateway (FastAPI)              │
│   CORS · request logging · auth · rate limiting  │
├──────────┬──────────┬──────────┬─────────────────┤
│ LLM      │ Embedding│ Search   │ Knowledge Graph │
│ Runtime  │ Service  │ Service  │ Engine          │
├──────────┴──────────┴──────────┴─────────────────┤
│              Agent Orchestrator (LangGraph)       │
├──────────────────────────────────────────────────┤
│              Shared Utilities                     │
│  SQLite · Qdrant · Logging · Security · Config   │
└──────────────────────────────────────────────────┘

┌───────────────────┐  ┌──────────────────┐
│ Ingestion Services│  │  Vector Services  │
│ PDF·DOCX·HTML·OCR │  │  Qdrant·LanceDB   │
│ Speech·Chunking   │  │                  │
└───────────────────┘  └──────────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| **Gateway** | 8100 | Central API gateway, routes to all sub-services |
| **LLM Runtime** | — | Ollama integration for chat, completions, model management |
| **Embedding** | — | sentence-transformers (BGE/E5/Nomic) embedding pipeline |
| **Search** | — | Hybrid search: vector similarity + BM25 + metadata filters |
| **Knowledge Graph** | — | Entity/relationship extraction and graph queries |
| **Agents** | — | LangGraph multi-agent orchestration |
| **Ingestion** | 8101 | File processing pipeline (PDF, DOCX, HTML, OCR, Speech) |
| **Vector** | 8102 | Vector database management (Qdrant embedded) |

## Quick Start

```bash
# Install dependencies
uv sync

# Run as monolith (all services in one process)
uv run uvicorn gateway.main:app --host 127.0.0.1 --port 8100

# Run individual services
uv run uvicorn ingestion-services.router:router_app --port 8101
uv run uvicorn vector-services.router:router_app --port 8102
```

## Project Structure

```
ai-services/
├── gateway/          # API gateway & middleware
├── llm_runtime/      # Ollama / llama.cpp integration
├── embedding/        # Embedding pipeline
├── search/           # Hybrid search engine
├── knowledge_graph/  # Knowledge graph engine
├── agents/           # LangGraph agent orchestration
├── shared/           # Shared utilities (DB, logging, security)
└── tests/            # Pytest test suite

ingestion-services/
├── parsers/          # PDF, DOCX, HTML, Markdown, TXT parsers
├── chunking/         # Semantic document chunking
├── ocr/              # PaddleOCR + Tesseract
├── speech/           # Whisper.cpp transcription
└── tests/

vector-services/
└── tests/
```

## Configuration

All configuration is via environment variables (`.env` file supported):

| Variable | Default | Description |
|----------|---------|-------------|
| `NODUS_HOST` | `127.0.0.1` | Bind address |
| `NODUS_PORT` | `8100` | Gateway port |
| `NODUS_LOG_LEVEL` | `info` | Log level |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Default embedding model |
| `QDRANT_PATH` | `./data/qdrant` | Qdrant storage path |
| `SQLITE_PATH` | `./data/nodus.db` | SQLite database path |
| `DATA_DIR` | `./data` | Root data directory |

## Testing

```bash
uv run pytest --cov -v
```
