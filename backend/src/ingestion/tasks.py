import uuid

from qdrant_client.http.models import PointStruct

from core.database import DatabaseManager


class IngestionPipeline:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    async def process_document(self, filename: str, content: bytes) -> str:
        """Parses document, chunks text, and sends to vector store."""
        # Stub: Only supports UTF-8 txt for now
        text = content.decode("utf-8", errors="ignore")

        # Naive chunking
        chunk_size = 500
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        # Embed chunks
        embeddings = self.db_manager.embed_model.encode(chunks)

        points = []
        doc_id = str(uuid.uuid4())

        for i, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=False)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb.tolist(),
                    payload={
                        "source_id": doc_id,
                        "filename": filename,
                        "chunk_index": i,
                        "text": chunk,
                    },
                )
            )

        await self.db_manager.qdrant_client.upsert(collection_name="nodus_memory", points=points)

        return doc_id
