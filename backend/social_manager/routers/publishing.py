import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime

from social_manager.db import SessionLocal, PostRepository, SocialConnectionRepository, Post, PublishingJob, SocialStrategyLogRepository, Asset
from social_manager.routers.users import get_current_user
from social_manager.platforms.hub import get_user_platform_hub
from social_manager.approvals import policy_engine, approval_workflow
from social_manager.copy_generator import CopyGenerator

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
    asset_ids: Optional[List[int]] = None
    scheduled_at: Optional[Any] = None

class HashtagGenerateRequest(BaseModel):
    description: str
    platform: str = "instagram"

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

    # Run Compliance Policy Checks
    policy_res = policy_engine.check_content(post_data.content)
    has_warnings = any(v.severity == "warning" for v in policy_res["violations"])
    
    # Set status & approval_status based on compliance outcome
    if not policy_res["passed"]:
        status = "draft"
        approval_status = "rejected"
    elif has_warnings:
        status = "draft"
        approval_status = "pending"
    else:
        status = "scheduled" if post_data.scheduled_at else "approved"
        approval_status = "approved"

    # Create the Post record
    post_repo = PostRepository(db)
    post = post_repo.create(
        user_id=user_id,
        content=post_data.content,
        scheduled_at=post_data.scheduled_at,
        status=status,
        approval_status=approval_status,
        asset_ids=post_data.asset_ids
    )
    
    strategy_log_repo = SocialStrategyLogRepository(db)
    
    # If policy check failed (errors)
    if not policy_res["passed"]:
        violations_str = ", ".join([v.details for v in policy_res["violations"]])
        strategy_log_repo.log_event(
            event="compliance_failure",
            details=f"Post ID {post.id} failed compliance checks. Violations: {violations_str}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Compliance Check Failed: {violations_str}"
        )
        
    # If warning
    if has_warnings:
        warnings_str = ", ".join([v.details for v in policy_res["violations"] if v.severity == "warning"])
        strategy_log_repo.log_event(
            event="compliance_warning",
            details=f"Post ID {post.id} created with compliance warnings (pending approval): {warnings_str}"
        )
        # Register in approval workflow
        approval_workflow.submit_for_approval(
            post_id=post.id,
            content=post.content,
            creator_id=str(user_id),
            required_approvers=["manager"]
        )
        
        # Create PublishingJobs for each platform (status=pending, but do not trigger background task execution)
        jobs = []
        for platform in post_data.platforms:
            job = PublishingJob(
                post_id=post.id,
                platform=platform,
                status="pending"
            )
            db.add(job)
            db.flush()
            jobs.append(job)
        db.commit()
        
        return {
            "status": "warning_pending_approval",
            "post_id": post.id,
            "job_ids": [j.id for j in jobs],
            "message": f"Post submitted but requires approval due to warnings: {warnings_str}"
        }

    # All checks passed (success/auto-approved)
    strategy_log_repo.log_event(
        event="compliance_passed",
        details=f"Post ID {post.id} passed all compliance checks (auto-approved)."
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

@router.post("/upload")
async def upload_media(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Cannot upload more than 10 files (Instagram limit).")
        
    saved_assets = []
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "avi", "mkv"]:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")
            
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        file_type = "video" if file_ext in ["mp4", "mov", "avi", "mkv"] else "image"
        db_asset = Asset(
            file_type=file_type,
            url=f"/static/uploads/{unique_filename}",
            alt_text=file.filename
        )
        db.add(db_asset)
        db.flush()
        
        saved_assets.append({
            "id": db_asset.id,
            "url": db_asset.url,
            "file_type": db_asset.file_type
        })
        
    db.commit()
    return saved_assets

@router.post("/generate-hashtags")
async def generate_hashtags(
    req: HashtagGenerateRequest,
    current_user = Depends(get_current_user)
):
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty.")
    try:
        generator = CopyGenerator()
        hashtags = generator.generate_hashtag_set(topic=req.description, platform=req.platform, size=10)
        return {"hashtags": hashtags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate hashtags: {str(e)}")

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

        # Fetch actual assets
        assets_list = []
        if post.asset_ids:
            assets_list = db_session.query(Asset).filter(Asset.id.in_(post.asset_ids)).all()

        # 1. Prepare
        prepared = await user_hub.prepare_post_for_platform(
            platform=job.platform,
            content=post.content,
            assets=[{"url": a.url, "file_type": a.file_type} for a in assets_list]
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
