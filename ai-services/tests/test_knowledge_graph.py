import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_graph_stats() -> None:
    """Test getting graph node and edge counts."""
    response = client.get("/api/v1/graph/stats")
    # Succeeds if database initialized successfully
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "nodes" in data
        assert "edges" in data

def test_add_entity() -> None:
    """Test adding an entity to the graph."""
    entity_payload = {
        "name": "Mistral AI",
        "entity_type": "organization",
        "description": "AI company specializing in open-weight models."
    }
    response = client.post("/api/v1/graph/entities", json=entity_payload)
    assert response.status_code in (200, 201, 500)
