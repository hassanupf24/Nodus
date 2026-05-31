import uuid
from typing import List, Dict, Any
from ingestion_services.chunking.schemas import Chunk

class SemanticChunker:
    """Chunks documents using semantic sentence boundaries and character overlaps."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str, source_metadata: Dict[str, Any]) -> List[Chunk]:
        if not text.strip():
            return []

        # Naive split by sentence end markers
        import re
        sentences = re.split(r"(?<=[.!?])\s+", text)
        
        chunks: List[Chunk] = []
        current_chunk_text = ""
        chunk_idx = 0

        for sentence in sentences:
            if len(current_chunk_text) + len(sentence) <= self.chunk_size:
                current_chunk_text += (" " if current_chunk_text else "") + sentence
            else:
                # Add old chunk
                if current_chunk_text:
                    chunks.append(self._create_chunk(current_chunk_text, chunk_idx, source_metadata))
                    chunk_idx += 1
                
                # Setup new chunk with overlap
                overlap_text = current_chunk_text[-self.overlap:] if len(current_chunk_text) > self.overlap else current_chunk_text
                # Find start of a sentence in the overlap to keep it clean
                space_idx = overlap_text.find(" ")
                if space_idx != -1:
                    overlap_text = overlap_text[space_idx + 1:]
                
                current_chunk_text = overlap_text + (" " if overlap_text else "") + sentence

        # Add remaining text
        if current_chunk_text.strip():
            chunks.append(self._create_chunk(current_chunk_text, chunk_idx, source_metadata))

        return chunks

    def _create_chunk(self, text: str, index: int, metadata: Dict[str, Any]) -> Chunk:
        merged_meta = {**metadata, "chunk_index": index}
        return Chunk(
            id=str(uuid.uuid4()),
            text=text,
            metadata=merged_meta,
            chunk_index=index
        )
