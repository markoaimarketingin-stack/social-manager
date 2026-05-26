from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime

from social_manager.db import SessionLocal, PostRepository, SocialConnectionRepository, Post, PublishingJob
from social_manager.routers.users import get_current_user
from social_manager.platforms.hub import get_user_platform_hub

router = APIRouter(prefix="/api/publishing", tags=["Publishing"])

# ── DB Dependency ─────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Schemas ───────────────────────────────────────────────────────────────────
class PostCreate(BaseModel):
    platforms: List[str]
    content: str
    asset_ids: Optional[Any] = None
    scheduled_at: Optional[Any] = None

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/schedule")
async def schedule_post(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule a post across multiple platforms.
    If no scheduled_at is provided, it attempts to publish immediately in the background.
    """
    body = await request.json()
    print(f"DEBUG: Received schedule_post body: {body}")
    try:
        post_data = PostCreate(**body)
    except Exception as e:
        print(f"DEBUG: Pydantic Validation Error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    conn_repo = SocialConnectionRepository(db)
    user_id = current_user.id
    
    # Check if user is connected to all requested platforms
    for platform in post_data.platforms:
        if not conn_repo.get_user_connection(user_id, platform):
            raise HTTPException(status_code=400, detail=f"No active connection found for {platform}")

    # Create the Post record
    post_repo = PostRepository(db)
    post = post_repo.create(
        user_id=user_id,
        content=post_data.content,
        scheduled_at=post_data.scheduled_at
    )
    
    # Create PublishingJobs for each platform
    jobs = []
    for platform in post_data.platforms:
        job = PublishingJob(
            post_id=post.id,
            platform=platform,
            status="scheduled" if post_data.scheduled_at else "pending"
        )
        db.add(job)
        db.flush()
        jobs.append(job)
    
    db.commit()

    # If immediate, trigger background task
    if not post_data.scheduled_at:
        for job in jobs:
            background_tasks.add_task(execute_publishing_job, job.id)

    return {
        "status": "success",
        "post_id": post.id,
        "job_ids": [j.id for j in jobs]
    }

@router.get("/queue")
async def get_queue(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the publishing queue for the current user."""
    posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()
    results = []
    for p in posts:
        jobs = db.query(PublishingJob).filter(PublishingJob.post_id == p.id).all()
        results.append({
            "id": p.id,
            "content": p.content,
            "scheduled_at": p.scheduled_at,
            "jobs": [{"platform": j.platform, "status": j.status, "error": j.error_message} for j in jobs]
        })
    return results

# ── Background Task Logic ─────────────────────────────────────────────────────

async def execute_publishing_job(job_id: int):
    """
    Background worker to execute a single publishing job.
    Uses the user-specific platform hub to dispatch the post.
    """
    db_session = SessionLocal()
    try:
        job = db_session.query(PublishingJob).filter(PublishingJob.id == job_id).first()
        if not job: return

        job.status = "processing"
        db_session.commit()
        
        post = job.post
        # Get the hub for this specific user
        user_hub = get_user_platform_hub(post.user_id, db_session)

        # 1. Prepare
        prepared = await user_hub.prepare_post_for_platform(
            platform=job.platform,
            content=post.content,
            assets=[]
        )
        
        # 2. Publish
        result = await user_hub.publish_to_platform(
            platform=job.platform,
            prepared_post=prepared
        )
        
        job.status = "published"
        job.platform_post_id = str(result.get("id", ""))
    except Exception as e:
        print(f"PUBLISHING ERROR for job {job_id}: {e}")
        job.status = "failed"
        job.error_message = str(e)
    finally:
        db_session.commit()
        db_session.close()
