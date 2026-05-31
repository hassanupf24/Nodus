from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from pydantic import BaseModel
from agents.orchestrator import AgentOrchestrator
from core.database import DatabaseManager
from ingestion.tasks import IngestionPipeline

app = FastAPI(title="Nodus Gateway", version="0.1.0")
db_manager = DatabaseManager()
ingestion_pipeline = IngestionPipeline(db_manager)

# We lazily initialize the orchestrator
orchestrator: AgentOrchestrator | None = None

@app.on_event("startup")
async def startup_event():
    global orchestrator
    orchestrator = AgentOrchestrator()
    await db_manager.init_sqlite()
    await db_manager.init_qdrant()

class ChatRequest(BaseModel):
    message: str
    context: dict | None = None

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/v1/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    content = await file.read()
    doc_id = await ingestion_pipeline.process_document(file.filename, content)
    return {"status": "success", "doc_id": doc_id}

@app.websocket("/api/v1/chat/stream")
async def chat_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            if message and orchestrator:
                # Stream the LangGraph execution back to the client
                async for chunk in orchestrator.process_stream(message):
                    await websocket.send_text(chunk)
                    
    except WebSocketDisconnect:
        pass
