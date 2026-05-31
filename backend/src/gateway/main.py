from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="Nodus Gateway", version="0.1.0")

class ChatRequest(BaseModel):
    message: str
    context: dict | None = None

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.websocket("/api/v1/chat/stream")
async def chat_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Stub: Send to LangGraph Orchestrator
            await websocket.send_json({"type": "token", "content": "Acknowledged"})
    except WebSocketDisconnect:
        pass
