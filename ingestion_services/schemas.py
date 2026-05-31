from pydantic import BaseModel, Field
from typing import List, Optional

class IngestionRequest(BaseModel):
    file_path: str = Field(..., description="Absolute local path to the target document or file")
    tags: List[str] = Field(default_factory=list, description="Metadata tags to assign to the ingested content")
    collection_name: str = Field(default="documents", description="Target vector database collection")

class IngestionJob(BaseModel):
    job_id: str
    file_name: str
    file_type: str
    file_size: int
    status: str = Field(..., description="One of: pending, processing, completed, failed")
    progress: int = Field(default=0, ge=0, le=100)
    started_at: float
    completed_at: Optional[float] = None
    error: Optional[str] = None
    chunks_count: Optional[int] = None
    entities_count: Optional[int] = None

class IngestionResult(BaseModel):
    job_id: str
    status: str
    chunks_count: int
    entities_count: int
    elapsed_ms: float
