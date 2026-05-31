import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ingestion_services.schemas import IngestionRequest, IngestionJob
from ingestion_services.service import IngestionService

router = APIRouter(prefix="/ingest", tags=["Ingestion Pipeline"])

# Shared instance singleton
_ingestion_service: Optional[IngestionService] = None

def get_ingestion_service() -> IngestionService:
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service

@router.post("", response_model=Dict[str, str])
async def start_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    svc: IngestionService = Depends(get_ingestion_service)
) -> Dict[str, str]:
    """Start an asynchronous document ingestion job."""
    job_id = str(uuid.uuid4())
    background_tasks.add_task(
        svc.ingest_file, 
        job_id=job_id, 
        file_path=request.file_path, 
        collection_name=request.collection_name
    )
    return {"job_id": job_id, "status": "processing"}

@router.get("/status/{job_id}", response_model=IngestionJob)
async def get_job_status(
    job_id: str,
    svc: IngestionService = Depends(get_ingestion_service)
) -> IngestionJob:
    """Retrieve details and progress of a specific ingestion job."""
    job = svc.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job

@router.get("/jobs", response_model=List[IngestionJob])
async def list_jobs(
    svc: IngestionService = Depends(get_ingestion_service)
) -> List[IngestionJob]:
    """List all recent and active ingestion tasks."""
    return svc.list_jobs()
