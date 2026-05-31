import pytest
from fastapi.testclient import TestClient
from ingestion_services.router import router
from ingestion_services.chunking.chunker import SemanticChunker
from ingestion_services.parsers import ParserRegistry
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_parser_registry() -> None:
    """Test that the parser registry returns the correct parsers."""
    pdf_parser = ParserRegistry.get_parser("test.pdf")
    assert pdf_parser.__class__.__name__ == "PDFParser"

    docx_parser = ParserRegistry.get_parser("test.docx")
    assert docx_parser.__class__.__name__ == "DOCXParser"

    txt_parser = ParserRegistry.get_parser("test.log")
    assert txt_parser.__class__.__name__ == "TextParser"

def test_semantic_chunker() -> None:
    """Test that the semantic chunker splits text with overlays."""
    chunker = SemanticChunker(chunk_size=50, overlap=10)
    text = "Nodus is local-first. It preserves security. It encrypts indices."
    chunks = chunker.split_text(text, {"source": "test"})
    assert len(chunks) > 0
    assert chunks[0].chunk_index == 0
    assert "Nodus" in chunks[0].text

def test_ingestion_api() -> None:
    """Test scheduling file ingestion background task."""
    payload = {
        "file_path": "nonexistent_file.pdf",
        "collection_name": "test_collection"
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"
