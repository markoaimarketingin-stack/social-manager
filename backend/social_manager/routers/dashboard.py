"""
Dashboard router — real-time stats for the current user.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from social_manager.db import SessionLocal, SocialConnectionRepository, Post, PublishingJob
from social_manager.routers.users import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
async def get_dashboard_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get real dashboard stats for the current user."""
    conn_repo = SocialConnectionRepository(db)
    connections = conn_repo.get_user_connections(current_user.id)
    
    # Get all posts for user
    posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()
    
    # Get all publishing jobs for user posts
    post_ids = [p.id for p in posts]
    jobs = []
    if post_ids:
        jobs = db.query(PublishingJob).filter(PublishingJob.post_id.in_(post_ids)).all()
    
    published_count = len([j for j in jobs if j.status == "published"])
    pending_count = len([j for j in jobs if j.status in ("pending", "scheduled", "processing")])
    failed_count = len([j for j in jobs if j.status == "failed"])
    
    recent_posts = []
    for post in posts[:10]:
        post_jobs = [j for j in jobs if j.post_id == post.id]
        recent_posts.append({
            "id": post.id,
            "content": post.content[:200] if post.content else "",
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "platforms": [{"platform": j.platform, "status": j.status, "error": j.error_message} for j in post_jobs]
        })
    
    connected_platforms = []
    for conn in connections:
        connected_platforms.append({
            "platform": conn.platform,
            "account_name": conn.platform_account_name,
            "account_id": conn.platform_account_id,
            "connected_at": conn.created_at.isoformat() if conn.created_at else None
        })
    
    return {
        "user": {"id": current_user.id, "email": current_user.email, "name": current_user.name},
        "connected_platforms": connected_platforms,
        "stats": {
            "total_posts": len(posts),
            "published": published_count,
            "pending": pending_count,
            "failed": failed_count
        },
        "recent_posts": recent_posts
    }
