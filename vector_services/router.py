from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from vector_services.schemas import CollectionCreate, UpsertRequest, SearchQuery
from vector_services.service import VectorService

router = APIRouter(prefix="/vector", tags=["Vector Operations"])

# Shared instance initialization
_vector_service: Optional[VectorService] = None

def get_vector_service() -> VectorService:
    global _vector_service
    if _vector_service is None:
        # Default storage folder inside local directory structure
        db_path = os.getenv("NODUS_QDRANT_PATH", "D:/projects/Nodus/data/qdrant")
        _vector_service = VectorService(db_path)
    return _vector_service

import os

@router.post("/collections")
def create_collection(
    config: CollectionCreate, 
    svc: VectorService = Depends(get_vector_service)
) -> Dict[str, Any]:
    """Create a new collection on the local Qdrant instance."""
    try:
        svc.create_collection(
            name=config.name, 
            vector_size=config.vector_size, 
            distance_metric=config.distance_metric
        )
        return {"status": "success", "message": f"Collection '{config.name}' created."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{name}/upsert")
def upsert_vectors(
    name: str, 
    request: UpsertRequest, 
    svc: VectorService = Depends(get_vector_service)
) -> Dict[str, Any]:
    """Upsert vectors into the specified collection."""
    try:
        count = svc.upsert_points(name, request.points)
        return {"status": "success", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{name}/search")
def search_vectors(
    name: str, 
    query: SearchQuery, 
    svc: VectorService = Depends(get_vector_service)
) -> List[Dict[str, Any]]:
    """Search nearest neighbor vectors in the collection."""
    try:
        return svc.search_points(
            collection_name=name, 
            vector=query.vector, 
            limit=query.limit, 
            score_threshold=query.score_threshold,
            filters=query.filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{name}")
def delete_collection(
    name: str, 
    svc: VectorService = Depends(get_vector_service)
) -> Dict[str, Any]:
    """Delete a collection and purge its vectors."""
    try:
        existed = svc.delete_collection(name)
        if not existed:
            raise HTTPException(status_code=404, detail="Collection not found")
        return {"status": "success", "message": f"Collection '{name}' deleted."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{name}/count")
def count_vectors(
    name: str, 
    svc: VectorService = Depends(get_vector_service)
) -> Dict[str, Any]:
    """Get the count of vector points inside the collection."""
    try:
        count = svc.count_points(name)
        return {"collection": name, "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
