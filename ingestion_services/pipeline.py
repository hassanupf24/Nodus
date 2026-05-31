import os
import time
from typing import Dict, Any, List
from ingestion_services.parsers import ParserRegistry
from ingestion_services.chunking.chunker import SemanticChunker
from embedding.service import get_embedding_service
from shared.vector_store import get_qdrant
from knowledge_graph.service import get_graph_service
from knowledge_graph.schemas import ExtractionRequest
from shared.logging_config import get_logger

logger = get_logger(__name__)

class IngestionPipeline:
    """Orchestrates document loading, parsing, chunking, embedding generation, and DB storage."""

    def __init__(self) -> None:
        self.chunker = SemanticChunker()

    async def run(self, file_path: str, collection_name: str = "documents") -> Dict[str, Any]:
        start_time = time.time()
        logger.info("ingestion.pipeline.start", file=file_path, collection=collection_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Parse Document
        parser = ParserRegistry.get_parser(file_path)
        parsed = parser.parse(file_path)
        text = parsed["text"]
        metadata = parsed["metadata"]
        
        # Add basic file metadata
        metadata["source"] = file_path
        metadata["created_at"] = os.path.getmtime(file_path)
        metadata["file_size"] = os.path.getsize(file_path)

        # 2. Chunk Document
        chunks = self.chunker.split_text(text, metadata)
        logger.info("ingestion.pipeline.chunked", chunks_count=len(chunks))

        if not chunks:
            return {
                "status": "completed",
                "chunks_count": 0,
                "entities_count": 0,
                "elapsed_ms": (time.time() - start_time) * 1000
            }

        # 3. Embed & Vector Store Chunks
        try:
            embed_svc = get_embedding_service()
            qdrant = get_qdrant()

            # Ensure collection exists
            qdrant.create_collection(collection_name, vector_size=384)

            vectors = []
            payloads = []
            ids = []

            for chunk in chunks:
                vec = await embed_svc.encode(chunk.text)
                vectors.append(vec)
                payloads.append(chunk.metadata)
                ids.append(chunk.id)

            qdrant.upsert(
                collection=collection_name,
                vectors=vectors,
                payloads=payloads,
                ids=ids
            )
            logger.info("ingestion.pipeline.vectors_stored", count=len(chunks))
        except Exception as e:
            logger.error("ingestion.pipeline.vector_store_failed", error=str(e))
            # Continue pipeline even if vector storage fails (graceful degradation)

        # 4. Extract Entities for Knowledge Graph
        entities_count = 0
        try:
            graph_svc = await get_graph_service()
            extraction_req = ExtractionRequest(
                text=text[:10000],  # Extract entities from first 10k chars to avoid LLM context overflow
                source=file_path,
                extract_relationships=True
            )
            resp = await graph_svc.extract_and_store(extraction_req)
            entities_count = len(resp.entities)
            logger.info("ingestion.pipeline.graph_stored", entities_count=entities_count)
        except Exception as e:
            logger.error("ingestion.pipeline.graph_store_failed", error=str(e))

        elapsed_ms = (time.time() - start_time) * 1000
        return {
            "status": "completed",
            "chunks_count": len(chunks),
            "entities_count": entities_count,
            "elapsed_ms": elapsed_ms
        }
