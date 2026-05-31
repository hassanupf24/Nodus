import time
import asyncio
from typing import Dict, Any, Optional
from ingestion_services.pipeline import IngestionPipeline
from ingestion_services.schemas import IngestionJob, IngestionResult
from shared.logging_config import get_logger

logger = get_logger(__name__)

class IngestionService:
    """Manages document ingestion jobs and execution telemetry."""

    def __init__(self) -> None:
        self.pipeline = IngestionPipeline()
        self._jobs: Dict[str, IngestionJob] = {}

    async def ingest_file(self, job_id: str, file_path: str, collection_name: str = "documents") -> None:
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1].replace(".", "")
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        job = IngestionJob(
            job_id=job_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            status="processing",
            progress=10,
            started_at=time.time()
        )
        self._jobs[job_id] = job
        logger.info("ingestion.service.job_registered", job_id=job_id, file=file_name)

        try:
            # Simulate progress increments for UI responsiveness
            await asyncio.sleep(0.1)
            job.progress = 30
            
            result = await self.pipeline.run(file_path, collection_name)
            
            job.progress = 100
            job.status = "completed"
            job.completed_at = time.time()
            job.chunks_count = result["chunks_count"]
            job.entities_count = result["entities_count"]
            logger.info("ingestion.service.job_completed", job_id=job_id)
        except Exception as e:
            logger.error("ingestion.service.job_failed", job_id=job_id, error=str(e))
            job.status = "failed"
            job.error = str(e)
            job.completed_at = time.time()

    def get_job_status(self, job_id: str) -> Optional[IngestionJob]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[IngestionJob]:
        return list(self._jobs.values())

import os
