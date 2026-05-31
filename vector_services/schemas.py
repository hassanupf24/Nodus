from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CollectionCreate(BaseModel):
    name: str = Field(..., description="The name of the vector database collection")
    vector_size: int = Field(default=384, description="Dimensionality of embeddings (default 384 for sentence-transformers)")
    distance_metric: str = Field(default="Cosine", description="Cosine, Dot, or Euclid distance")

class VectorPoint(BaseModel):
    id: str | int = Field(..., description="Unique UUID or integer ID for the point")
    vector: List[float] = Field(..., description="Dense embedding vector array")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary to store alongside vector")

class UpsertRequest(BaseModel):
    points: List[VectorPoint]

class SearchQuery(BaseModel):
    vector: List[float] = Field(..., description="Dense query vector")
    limit: int = Field(default=5, ge=1, le=100)
    score_threshold: Optional[float] = None
    filters: Optional[Dict[str, Any]] = None
