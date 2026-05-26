"""
Publishing queue and background worker.
Handles draft → scheduled → published workflow with retries and idempotency.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class PublishingJob:
    """Represents a single publishing task."""
    
    def __init__(self, post_id: int, user_id: int, platform: str, content: str, assets: List[Dict],
                 scheduled_at: Optional[datetime] = None, max_retries: int = 3):
        self.id = str(uuid.uuid4())
        self.idempotency_key = f"{post_id}_{platform}_{uuid.uuid4().hex[:8]}"
        self.post_id = post_id
        self.user_id = user_id
        self.platform = platform
        self.content = content
        self.assets = assets
        self.scheduled_at = scheduled_at
        self.max_retries = max_retries
        self.attempt_count = 0
        self.status = JobStatus.PENDING
        self.created_at = datetime.utcnow()
        self.published_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.platform_post_id: Optional[str] = None
        self.preview_url: Optional[str] = None
    
    def mark_in_progress(self):
        self.status = JobStatus.IN_PROGRESS
        self.attempt_count += 1
    
    def mark_published(self, platform_post_id: str, preview_url: str):
        self.status = JobStatus.PUBLISHED
        self.platform_post_id = platform_post_id
        self.preview_url = preview_url
        self.published_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        self.error_message = error
        if self.attempt_count >= self.max_retries:
            self.status = JobStatus.FAILED
        else:
            self.status = JobStatus.PENDING  # Retry
    
    def is_ready_to_publish(self) -> bool:
        """Check if job should be published now."""
        if self.status != JobStatus.PENDING:
            return False
        
        if self.scheduled_at:
            return datetime.utcnow() >= self.scheduled_at
        
        return True
    
    def can_retry(self) -> bool:
        """Check if retry is possible."""
        return self.attempt_count < self.max_retries


class PublishingQueue:
    """
    In-memory publishing queue with async worker support.
    Design ready for external queues (Redis, RabbitMQ, Celery).
    """
    
    def __init__(self, max_workers: int = 5):
        self.pending_jobs: Dict[str, PublishingJob] = {}
        self.completed_jobs: Dict[str, PublishingJob] = {}
        self.failed_jobs: Dict[str, PublishingJob] = {}
        self.max_workers = max_workers
        self._worker_tasks = []
        self._running = False
    
    def enqueue(self, job: PublishingJob) -> str:
        """Add job to queue."""
        self.pending_jobs[job.id] = job
        logger.info(f"Enqueued publishing job {job.id} for post {job.post_id}")
        return job.id
    
    def get_job(self, job_id: str) -> Optional[PublishingJob]:
        """Get job by ID from any queue."""
        return (self.pending_jobs.get(job_id) or 
                self.completed_jobs.get(job_id) or 
                self.failed_jobs.get(job_id))
    
    def get_pending_jobs(self) -> List[PublishingJob]:
        """Get all pending jobs ready to publish."""
        return [j for j in self.pending_jobs.values() if j.is_ready_to_publish()]
    
    def move_to_completed(self, job_id: str):
        """Move job from pending to completed."""
        if job_id in self.pending_jobs:
            job = self.pending_jobs.pop(job_id)
            self.completed_jobs[job_id] = job
    
    def move_to_failed(self, job_id: str):
        """Move job from pending to failed."""
        if job_id in self.pending_jobs:
            job = self.pending_jobs.pop(job_id)
            self.failed_jobs[job_id] = job
    
    async def start_workers(self, publish_handler):
        """Start background workers."""
        self._running = True
        logger.info(f"Starting {self.max_workers} publishing workers")
        
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker_loop(i, publish_handler))
            self._worker_tasks.append(task)
    
    async def stop_workers(self):
        """Stop background workers."""
        self._running = False
        for task in self._worker_tasks:
            task.cancel()
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        logger.info("Publishing workers stopped")
    
    async def _worker_loop(self, worker_id: int, publish_handler):
        """Single worker processing loop."""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                job = self._get_next_job()
                if not job:
                    await asyncio.sleep(1)  # Poll every second
                    continue
                
                logger.info(f"Worker {worker_id} processing job {job.id}")
                await self._process_job(job, publish_handler)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(2)
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _get_next_job(self) -> Optional[PublishingJob]:
        """Get next job ready for processing (FIFO)."""
        for job in self.pending_jobs.values():
            if job.is_ready_to_publish() and job.status == JobStatus.PENDING:
                return job
        return None
    
    async def _process_job(self, job: PublishingJob, publish_handler):
        """Process single job with error handling and retries."""
        job.mark_in_progress()
        
        try:
            # Call platform-specific publish handler
            result = await publish_handler(job)
            job.mark_published(result["platform_post_id"], result.get("preview_url", ""))
            self.move_to_completed(job.id)
            logger.info(f"Job {job.id} published successfully")
            
        except Exception as e:
            error_msg = str(e)
            job.mark_failed(error_msg)
            
            if job.can_retry():
                # Put back in pending for retry
                logger.warning(f"Job {job.id} failed (attempt {job.attempt_count}/{job.max_retries}): {error_msg}")
            else:
                self.move_to_failed(job.id)
                logger.error(f"Job {job.id} failed permanently: {error_msg}")


class PublishingService:
    """High-level service coordinating publishing workflow."""
    
    def __init__(self, queue: PublishingQueue):
        self.queue = queue
    
    async def schedule_post(self, post_id: int, user_id: int, platform: str, content: str, 
                           assets: List[Dict], schedule_time: Optional[datetime] = None) -> Dict:
        """
        Schedule a post for publishing.
        
        Returns: {job_id, status, scheduled_at}
        """
        job = PublishingJob(
            post_id=post_id,
            user_id=user_id,
            platform=platform,
            content=content,
            assets=assets,
            scheduled_at=schedule_time
        )
        
        job_id = self.queue.enqueue(job)
        
        return {
            "job_id": job_id,
            "status": "scheduled",
            "scheduled_at": schedule_time.isoformat() if schedule_time else None,
            "idempotency_key": job.idempotency_key,
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get publishing job status."""
        job = self.queue.get_job(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.id,
            "post_id": job.post_id,
            "platform": job.platform,
            "status": job.status.value,
            "attempt_count": job.attempt_count,
            "max_retries": job.max_retries,
            "published_at": job.published_at.isoformat() if job.published_at else None,
            "platform_post_id": job.platform_post_id,
            "preview_url": job.preview_url,
            "error_message": job.error_message,
        }
    
    def get_pending_jobs(self) -> List[Dict]:
        """Get all pending jobs."""
        return [
            {
                "job_id": j.id,
                "post_id": j.post_id,
                "platform": j.platform,
                "status": j.status.value,
                "scheduled_at": j.scheduled_at.isoformat() if j.scheduled_at else None,
            }
            for j in self.queue.get_pending_jobs()
        ]


# Global instances
publishing_queue = PublishingQueue(max_workers=5)
publishing_service = PublishingService(publishing_queue)
