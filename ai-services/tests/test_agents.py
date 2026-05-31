import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_list_agents() -> None:
    """Test retrieving list of registered agents."""
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) >= 3
    names = [a["name"] for a in agents]
    assert "research" in names
    assert "memory" in names
    assert "summarizer" in names

def test_invoke_agent_invalid() -> None:
    """Test invoking a non-existent agent raises error."""
    payload = {
        "query": "hello",
        "agent_name": "ghost_agent"
    }
    response = client.post("/api/v1/agents/invoke", json=payload)
    assert response.status_code == 500

def test_invoke_summarizer_agent() -> None:
    """Test invoking the summarizer agent."""
    payload = {
        "query": "Nodus is an offline-first private memory application. It runs locally.",
        "agent_name": "summarizer"
    }
    response = client.post("/api/v1/agents/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "summarizer"
    assert "response" in data
    assert data["status"] in ("completed", "degraded")
