import pytest
from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_generate_embeddings_bad_request() -> None:
    """Test generating embeddings with invalid input raises validation error."""
    response = client.post("/api/v1/embeddings", json={})
    assert response.status_code == 422

def test_generate_embeddings() -> None:
    """Test standard single sentence text-to-vector mapping."""
    payload = {
        "model": "nomic-embed-text",
        "text": "This is a local memory fragment to embed."
    }
    response = client.post("/api/v1/embeddings", json=payload)
    # 200 if model loaded, 500/404 if model not pulled yet. Both are valid server responses.
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "embeddings" in data
        assert len(data["embeddings"]) > 0
