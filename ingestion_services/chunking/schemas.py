from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Chunk(BaseModel):
    id: str = Field(..., description="Unique UUID for this text chunk")
    text: str = Field(..., description="The chunk text fragment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata tags, source file paths, and indexes")
    chunk_index: int = Field(..., description="Position index of the chunk in the document")
    embedding: Optional[List[float]] = Field(None, description="Optional dense embedding vector representation")
