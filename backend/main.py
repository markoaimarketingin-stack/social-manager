from __future__ import annotations
import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from social_manager.state import SocialManagerState
from social_manager.graph import build_social_strategy
from social_manager.db import init_db
from social_manager.config import settings
from social_manager.workers import init_workers, shutdown_workers, publishing_service
from social_manager.approvals import policy_engine, approval_workflow, UserRole, RoleBasedAccessControl
from social_manager.analytics import metrics_service, kpi_computer, dashboard_generator
from social_manager.knowledge_base import KnowledgeBaseManager, init_knowledge_base_with_samples
from social_manager.feature_endpoints import all_feature_routers
from social_manager.real_features_endpoints import all_real_feature_routers
from social_manager.routers.auth import router as auth_router
from social_manager.routers.users import router as users_router, get_current_user
from social_manager.routers.publishing import router as publishing_router
from social_manager.routers.strategy import router as strategy_router
from social_manager.routers.chat import router as chat_router
from social_manager.routers.v1_compat import router as v1_compat_router
from social_manager.db import SocialConnectionRepository, SessionLocal

from fastapi import UploadFile, File
import shutil

logger = logging.getLogger(__name__)

# ===== LIFECYCLE MANAGEMENT =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown handling."""
    # Startup
    logger.info("✓ Starting Social Manager...")
    init_db(seed=42)
    init_knowledge_base_with_samples()  # Load sample documents
    await init_workers(
        platform_credentials={
            "twitter_api_key": settings.twitter_api_key or "",
            "twitter_api_secret": settings.twitter_api_secret or "",
            "twitter_access_token": settings.twitter_access_token or "",
            "twitter_access_token_secret": settings.twitter_access_token_secret or "",
            "linkedin_access_token": settings.linkedin_access_token or "",
            "linkedin_client_id": settings.linkedin_client_id or "",
            "linkedin_client_secret": settings.linkedin_client_secret or "",
            "instagram_access_token": settings.instagram_access_token or "",
            "instagram_business_account_id": settings.instagram_business_account_id or "",
        },
        sandbox_mode=False  # Auto-detect per adapter
    )
    yield
    # Shutdown
    logger.info("✓ Shutting down Social Manager...")
    await shutdown_workers()


app = FastAPI(title="Social Manager Agent", version="0.1.0", lifespan=lifespan)

# CORS: Restrict to localhost + envvar-configurable origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8088",
        "https://social-community-manager.vercel.app",
        "https://social-community-manager-git-dev-arpit-fixes.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# ===== REQUEST/RESPONSE MODELS =====

class RunRequest(BaseModel):
    state: SocialManagerState

class RunResponse(BaseModel):
    state: SocialManagerState

class AdjustRequest(BaseModel):
    state: SocialManagerState
    instruction: str

class SchedulePostRequest(BaseModel):
    post_id: int
    platform: str
    content: str
    assets: List[dict] = []
    scheduled_at: Optional[datetime] = None

class ApprovalRequest(BaseModel):
    post_id: int
    approver_id: str
    approved: bool
    notes: Optional[str] = None
    platform: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None

class PolicyCheckRequest(BaseModel):
    content: str

# ===== CORE WORKFLOW ENDPOINTS =====

@app.post("/api/social_manager/run", response_model=RunResponse)
async def run_graph(req: RunRequest):
    """Run full social strategy generation pipeline."""
    out = build_social_strategy(req.state)
    return RunResponse(state=out)

@app.post("/api/social_manager/adjust", response_model=RunResponse)
async def adjust_and_run(req: AdjustRequest):
    """Apply conversational adjustments and re-run."""
    inst = req.instruction.lower()
    st = req.state
    st.conversation_history.append({"role": "user", "content": req.instruction})
    
    # === POSTING FREQUENCY ADJUSTMENTS ===
    if "focus more on instagram" in inst or "instagram" in inst and "more" in inst:
        if "Instagram" not in st.active_platforms:
            st.active_platforms.append("Instagram")
        st.posting_frequency["Instagram"] = max(st.posting_frequency.get("Instagram", 3), 5)
        # Boost Instagram-aligned pillars
        for pillar in st.content_pillars:
            if pillar.name in ["Product usage", "Offers & launches", "Community highlights"]:
                pillar.weight = min(pillar.weight * 1.3, 2.0)
    
    if "focus more on linkedin" in inst or "linkedin" in inst and "more" in inst:
        if "LinkedIn" not in st.active_platforms:
            st.active_platforms.append("LinkedIn")
        st.posting_frequency["LinkedIn"] = max(st.posting_frequency.get("LinkedIn", 2), 4)
        # Boost LinkedIn-aligned pillars
        for pillar in st.content_pillars:
            if pillar.name in ["Education", "Behind-the-scenes", "Transformation stories"]:
                pillar.weight = min(pillar.weight * 1.3, 2.0)
    
    if "focus more on x" in inst or "twitter" in inst or ("x" in inst and "more" in inst):
        if "X" not in st.active_platforms:
            st.active_platforms.append("X")
        st.posting_frequency["X"] = max(st.posting_frequency.get("X", 3), 5)
        # Boost X-aligned pillars (engagement, quick tips)
        for pillar in st.content_pillars:
            if pillar.name in ["Education", "Community highlights"]:
                pillar.weight = min(pillar.weight * 1.3, 2.0)
    
    # === CONTENT STRATEGY ADJUSTMENTS ===
    if "reduce promotional posts" in inst:
        st.structured_context["promo_reduce"] = True
        # Lower promotional pillar weight
        for pillar in st.content_pillars:
            if pillar.name == "Offers & launches":
                pillar.weight = max(pillar.weight * 0.5, 0.3)
    
    if "increase engagement" in inst:
        st.structured_context["engagement_boost"] = True
        # Boost engagement-focused pillars
        for pillar in st.content_pillars:
            if pillar.name in ["Community highlights", "Education", "Behind-the-scenes"]:
                pillar.weight = min(pillar.weight * 1.3, 2.0)
        if st.engagement_plan:
            st.engagement_plan.poll_ideas.append("This or That weekly")
            st.engagement_plan.weekly_live = "Twice weekly live with co-host"
    
    if "aggressive brand building" in inst:
        st.structured_context["aggressive_mode"] = True
        # Increase all frequencies
        for k in st.active_platforms:
            st.posting_frequency[k] = max(st.posting_frequency.get(k, 3), 6)
        # Boost all pillars
        for pillar in st.content_pillars:
            pillar.weight = min(pillar.weight * 1.4, 2.0)
        if st.engagement_metrics:
            st.engagement_metrics.post_consistency_score = 0.9
    
    if "festive" in inst or "season" in inst or "holiday" in inst:
        st.structured_context["seasonal_bias"] = True
        # Boost conversion and community pillars for holidays
        for pillar in st.content_pillars:
            if pillar.name in ["Offers & launches", "Community highlights"]:
                pillar.weight = min(pillar.weight * 1.4, 2.0)
    
    # === TONE & APPROACH ADJUSTMENTS ===
    if "educational" in inst or "expert" in inst or "thought leader" in inst:
        for pillar in st.content_pillars:
            if pillar.name == "Education":
                pillar.weight = min(pillar.weight * 1.5, 2.0)
    
    if "casual" in inst or "fun" in inst or "entertaining" in inst:
        for pillar in st.content_pillars:
            if pillar.name in ["Community highlights", "Behind-the-scenes"]:
                pillar.weight = min(pillar.weight * 1.3, 2.0)
    
    if "conversions" in inst or "sales" in inst or "revenue" in inst:
        for pillar in st.content_pillars:
            if pillar.name in ["Offers & launches", "Product usage"]:
                pillar.weight = min(pillar.weight * 1.4, 2.0)
    
    # Regenerate strategy with adjusted weights
    out = build_social_strategy(st)
    return RunResponse(state=out)

# (Deprecated endpoints removed)

# ===== METRICS & ANALYTICS =====

@app.get("/api/metrics/post/{post_id}")
async def get_post_metrics(post_id: str):
    """Get metrics for a specific post."""
    metrics = metrics_service.get_metrics_for_post(post_id)
    if not metrics:
        return {"metrics": [], "kpis": {}}
    
    kpis = kpi_computer.compute_campaign_kpis([metrics])
    return {"metrics": metrics, "kpis": kpis}

@app.get("/api/metrics/platform/{platform}")
async def get_platform_metrics(platform: str, hours: int = 24):
    """Get metrics for a platform."""
    metrics = metrics_service.get_metrics_for_platform(platform, hours)
    return {"platform": platform, "period_hours": hours, "metrics": metrics}

@app.get("/api/dashboard/campaign/{campaign_id}")
async def get_campaign_dashboard(campaign_id: int):
    """Get analytics dashboard for campaign."""
    metrics = {}
    kpis = {}
    return dashboard_generator.generate_summary(campaign_id, metrics, kpis)

# ===== COMMUNITY MANAGEMENT =====

@app.get("/api/inbox")
async def get_inbox():
    """Get community inbox (mentions, DMs, comments)."""
    return {
        "conversations": [],
    }

@app.post("/api/inbox/{conversation_id}/respond")
async def respond_to_conversation(conversation_id: int, response: str):
    """Send response to community conversation."""
    return {"conversation_id": conversation_id, "response_sent": True}

# ===== COMPLIANCE & POLICY =====

@app.post("/api/policy/check")
async def check_policy(req: PolicyCheckRequest):
    """Check content against policies."""
    result = policy_engine.check_content(req.content)
    return {
        "violations": [v.to_dict() for v in result["violations"]],
        "required_disclosures": result["required_disclosures"],
        "passed": result["passed"],
    }

class BatchApprovalRequest(BaseModel):
    entries: List[Dict]
    user_id: str

@app.post("/api/approvals/request-batch")
async def request_batch_approval(req: BatchApprovalRequest):
    """Submit a batch of entries for approval."""
    import time
    batch_id = f"BATCH{int(time.time())}"
    # For now, just return the batch_id as mock submission
    return {"status": "submitted", "batch_id": batch_id, "count": len(req.entries)}

@app.get("/api/approvals/pending")
async def get_pending_approvals(user_id: str):
    """Get pending approvals for user."""
    approvals = approval_workflow.get_pending_approvals_for_user(user_id)
    return {"pending_approvals": approvals}

# ===== HEALTH & SYSTEM =====

def _accepts_html_first(request: Request) -> bool:
    """Browsers send text/html first; API clients often send application/json or */*."""
    accept = request.headers.get("accept")
    if not accept or accept.strip() == "*/*":
        return False
    first = accept.split(",")[0].split(";")[0].strip().lower()
    return first == "text/html"


@app.get("/health")
async def health(request: Request):
    if _accepts_html_first(request):
        return HTMLResponse(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'/>"
            "<title>Health — Social Manager</title></head>"
            "<body style='font-family:system-ui,sans-serif;padding:2rem;line-height:1.5;color:#111'>"
            "<h1 style='font-size:1.25rem'>Backend is running</h1>"
            "<p>JSON status: <code>{\"status\": \"ok\"}</code></p>"
            "<p>This URL is for health checks. <strong>Open the app:</strong> "
            "<a href='/'>http://localhost:8088/</a></p></body></html>"
        )
    return JSONResponse(content={"status": "ok"})

@app.get("/api/system/status")
async def system_status():
    """Get system status."""
    return {
        "database": "connected",
        "workers": "running",
        "queue_pending": len(publishing_service.queue.pending_jobs),
    }

@app.post("/api/system/seed-dummy-data")
async def seed_dummy_data():
    """Seed the database with dummy data for testing."""
    import subprocess
    import sys
    try:
        seed_script = os.path.join(os.path.dirname(__file__), "social_manager", "seed_dummy_data.py")
        subprocess.run([sys.executable, seed_script], check=True)
        return {"status": "success", "message": "Dummy data seeded successfully"}
    except Exception as e:
        logger.error(f"Failed to seed dummy data: {e}")
        raise HTTPException(status_code=500, detail="Failed to seed dummy data")

# ===== KNOWLEDGE BASE MANAGEMENT =====

kb_manager = KnowledgeBaseManager()

class DocumentUploadRequest(BaseModel):
    category: str = "General"
    description: Optional[str] = None

@app.post("/api/knowledge_base/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "General",
    description: Optional[str] = None
):
    """Upload a document to the knowledge base.
    
    Supported formats: PDF, DOCX, TXT, CSV
    
    Returns: Document metadata with ID
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_uploads/{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Determine file type from extension
        file_type = file.filename.split(".")[-1].lower()
        
        # Add to knowledge base
        doc = kb_manager.add_document(
            file_path=temp_path,
            filename=file.filename,
            category=category,
            file_type=file_type
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "category": doc.category,
            "file_type": doc.file_type,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "content_length": len(doc.content) if doc.content else 0,
            "status": doc.processing_status
        }
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/knowledge_base/documents")
async def list_documents(category: Optional[str] = None, skip: int = 0, limit: int = 100):
    """List all documents in the knowledge base.
    
    Query parameters:
    - category: Filter by category (optional)
    - skip: Pagination skip (default: 0)
    - limit: Pagination limit (default: 100)
    """
    try:
        docs = kb_manager.get_documents(category=category)
        
        # Apply pagination
        paginated = docs[skip : skip + limit]
        
        return {
            "total": len(docs),
            "returned": len(paginated),
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "category": doc.category,
                    "file_type": doc.file_type,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "content_length": len(doc.content) if doc.content else 0,
                    "status": doc.processing_status
                }
                for doc in paginated
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@app.get("/api/knowledge_base/search")
async def search_documents(
    query: str,
    category: Optional[str] = None,
    limit: int = 10
):
    """Search documents in the knowledge base.
    
    Query parameters:
    - query: Search keywords (required)
    - category: Filter by category (optional)
    - limit: Max results to return (default: 10)
    """
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        results = kb_manager.search_documents(query=query, category=category)
        
        # Apply limit
        results = results[:limit]
        
        return {
            "query": query,
            "category": category,
            "results_count": len(results),
            "results": [
                {
                    "id": r["id"],
                    "filename": r["filename"],
                    "category": r["category"],
                    "file_type": r["type"],
                    "content_snippet": r.get("content_preview", ""),
                    "relevance_score": r["relevance_score"]
                }
                for r in results
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/api/knowledge_base/{doc_id}")
async def get_document(doc_id: int):
    """Get full content of a specific document."""
    try:
        docs = kb_manager.get_documents()
        doc = next((d for d in docs if d.id == doc_id), None)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "category": doc.category,
            "file_type": doc.file_type,
            "content": doc.content,
            "metadata": doc.doc_metadata,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "status": doc.processing_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@app.delete("/api/knowledge_base/{doc_id}")
async def delete_document(doc_id: int):
    """Delete a document from the knowledge base."""
    try:
        kb_manager.delete_document(doc_id)
        return {"id": doc_id, "deleted": True}
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.get("/api/knowledge_base/context/llm")
async def get_llm_context(category: Optional[str] = None, max_chars: int = 8000):
    """Get formatted knowledge base context for LLM injection.
    
    Query parameters:
    - category: Specific category to include (optional)
    - max_chars: Maximum character length (default: 8000)
    """
    try:
        context = kb_manager.build_context_for_llm(
            category=category,
            max_chars=max_chars
        )
        
        return {
            "context": context,
            "length": len(context),
            "max_chars": max_chars,
            "truncated": len(context) >= max_chars
        }
    except Exception as e:
        logger.error(f"Failed to build LLM context: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to build context")

# ===== PLATFORM STATUS =====

from fastapi import Depends
@app.get("/api/platforms/status")
async def get_platform_status(current_user = Depends(get_current_user)):
    """Get connection status for all platforms for the logged-in user."""
    db = SessionLocal()
    repo = SocialConnectionRepository(db)
    user_conns = repo.get_user_connections(current_user.id)
    db.close()
    
    # Map DB connections to status
    status_map = {}
    for c in user_conns:
        status_map[c.platform] = {
            "status": "connected",
            "account_name": c.platform_account_name
        }
    return {"platforms": status_map}

@app.get("/api/publishing/job/{job_id}")
async def get_publishing_job(job_id: str):
    """Get status of a publishing job."""
    status = publishing_service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

# ===== ROOT HEALTH REDIRECT =====

@app.get("/")
async def root():
    """API root — frontend runs separately on port 5173 (npm run dev)."""
    return JSONResponse({
        "service": "Social Community Manager API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "frontend": "http://localhost:5173"
    })

# ===== FEATURE ROUTERS (NEW INTELLIGENCE FEATURES) =====
# Include all new feature routers: Trends, Competitors, Segmentation, Positioning, Copy
for router in all_feature_routers:
    app.include_router(router)

# ===== REAL FEATURE ROUTERS (NEW INTEGRATIONS) =====
# Include all real feature routers: Real Trends, Sentiment, Images, Email, Influencers, Hashtags, A/B Tests, Metrics
for router in all_real_feature_routers:
    app.include_router(router)

# ===== AUTH ROUTERS (OAUTH & JWT) =====
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(publishing_router)
app.include_router(strategy_router)
app.include_router(chat_router)

# ===== V1 COMPATIBILITY ROUTER (FOR NEW FRONTEND) =====
app.include_router(v1_compat_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)
