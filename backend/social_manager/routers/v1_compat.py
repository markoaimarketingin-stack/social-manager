"""
Compatibility Router — /api/v1/ endpoints for the new frontend.

The new frontend was built against a workspace-scoped, /api/v1/ REST API.
This module provides those endpoints on top of the original backend so that
the frontend and backend integrate seamlessly.

Data is stored in an in-memory dict keyed by workspace ID.
For MVP / demo this is sufficient; production should migrate to real DB tables.
"""

from __future__ import annotations

import uuid
import copy
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rid(prefix: str = "id") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _add_days(days: int) -> str:
    return (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

# ---------------------------------------------------------------------------
# In-memory workspace store (demo-grade persistence)
# ---------------------------------------------------------------------------

_workspaces: Dict[str, Dict[str, Any]] = {}

def _ensure_workspace(ws_id: str) -> Dict[str, Any]:
    if ws_id not in _workspaces:
        ts = _now()
        _workspaces[ws_id] = {
            "id": ws_id,
            "name": "Default Workspace",
            "slug": "default-workspace",
            "brand_profile_id": None,
            "member_count": 1,
            "audience_segment_count": 0,
            "created_at": ts,
            "updated_at": ts,
            # sub-collections
            "brand_profile": None,
            "audience_segments": [],
            "strategies": [],
            "content_plans": [],
            "drafts": [],
            "workflow_runs": [],
            "activity": [],
            "knowledge_base_documents": [],
            "training_jobs": [],
        }
    return _workspaces[ws_id]

# ---------------------------------------------------------------------------
# Request / Response schemas (matching frontend expectations)
# ---------------------------------------------------------------------------

class CreateWorkspaceRequest(BaseModel):
    name: str
    owner: Optional[Dict[str, str]] = None

class UpsertBrandProfileRequest(BaseModel):
    brand_name: str
    industry: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    voice_summary: Optional[str] = None
    mission: Optional[str] = None

class AudienceSegmentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    age_range: Optional[str] = None
    interests: List[str] = []
    primary_platform: Optional[str] = None
    messaging_angle: Optional[str] = None

class StartStrategyRunRequest(BaseModel):
    goal: str = "Generate brand strategy"
    initiated_by_member_id: Optional[str] = None

class ReviewStrategyRequest(BaseModel):
    status: str
    review_notes: Optional[str] = None
    reviewer_member_id: Optional[str] = None

class StartContentPlanRunRequest(BaseModel):
    brand_strategy_id: Optional[str] = None
    planning_horizon_label: str = "Next 2 weeks"
    initiated_by_member_id: Optional[str] = None

class UpdatePlannedPostRequest(BaseModel):
    scheduled_for: Optional[str] = None
    platform: Optional[str] = None
    format: Optional[str] = None
    title: Optional[str] = None
    hook: Optional[str] = None
    angle: Optional[str] = None
    call_to_action: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    reviewer_member_id: Optional[str] = None

class StartDraftRunRequest(BaseModel):
    content_plan_id: Optional[str] = None
    initiated_by_member_id: Optional[str] = None

class UpdateDraftRequest(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    creative_brief: Optional[str] = None
    call_to_action: Optional[str] = None
    hashtags: Optional[List[str]] = None
    review_status: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewer_member_id: Optional[str] = None
    scheduled_publish_at: Optional[str] = None

class MarkPublishReadyRequest(BaseModel):
    reviewer_member_id: Optional[str] = None
    scheduled_publish_at: Optional[str] = None

class PublishDraftRequest(BaseModel):
    reviewer_member_id: Optional[str] = None

class UploadKBDocumentRequest(BaseModel):
    file_name: str
    category: str
    mime_type: str = "application/octet-stream"
    size_bytes: int = 0
    uploaded_by_member_id: Optional[str] = None

class QueueTrainingRequest(BaseModel):
    document_ids: List[str]
    category: str
    requested_by_member_id: Optional[str] = None

class AssistantCommandRequest(BaseModel):
    prompt: str
    route_context: str = "workspace"
    mode: str = "ask"
    attached_document_ids: Optional[List[str]] = None

# ---------------------------------------------------------------------------
# Activity helper
# ---------------------------------------------------------------------------

def _add_activity(ws: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
    ts = _now()
    event = {
        "id": _rid("activity"),
        "workspace_id": ws["id"],
        "actor_member_id": kwargs.get("actor_member_id"),
        "actor_label": kwargs.get("actor_label", "System"),
        "entity_type": kwargs.get("entity_type", "workspace"),
        "entity_id": kwargs.get("entity_id"),
        "event_type": kwargs.get("event_type", "unknown"),
        "summary": kwargs.get("summary", ""),
        "metadata_payload": kwargs.get("metadata_payload", {}),
        "created_at": ts,
        "updated_at": ts,
    }
    ws["activity"].insert(0, event)
    return event

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1", tags=["v1-compat"])

# ── System / Health ─────────────────────────────────────────────────────────

@router.get("/health")
async def v1_health():
    return {"status": "ok", "service": "social-manager-api"}

@router.get("/system/status")
async def v1_system_status():
    return {
        "status": "ok",
        "service": "social-manager-api",
        "environment": "development",
        "database": "connected",
    }

# ── Workspaces ──────────────────────────────────────────────────────────────

@router.post("/workspaces", status_code=201)
async def create_workspace(req: CreateWorkspaceRequest):
    ws_id = _rid("ws")
    ts = _now()
    slug = req.name.lower().replace(" ", "-")
    ws = _ensure_workspace(ws_id)
    ws.update(name=req.name, slug=slug, created_at=ts, updated_at=ts)
    _add_activity(ws, actor_label=req.owner.get("full_name", "User") if req.owner else "User",
                  entity_type="workspace", entity_id=ws_id,
                  event_type="workspace_created",
                  summary=f"Created workspace '{req.name}'.")
    return {k: v for k, v in ws.items() if k in (
        "id", "name", "slug", "brand_profile_id", "member_count",
        "audience_segment_count", "created_at", "updated_at")}

@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    ws["audience_segment_count"] = len(ws["audience_segments"])
    ws["brand_profile_id"] = ws["brand_profile"]["id"] if ws["brand_profile"] else None
    return {k: v for k, v in ws.items() if k in (
        "id", "name", "slug", "brand_profile_id", "member_count",
        "audience_segment_count", "created_at", "updated_at")}

# ── Brand Profile ───────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/brand-profile")
async def get_brand_profile(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    if not ws["brand_profile"]:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return ws["brand_profile"]

@router.put("/workspaces/{workspace_id}/brand-profile")
async def upsert_brand_profile(workspace_id: str, req: UpsertBrandProfileRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    if ws["brand_profile"]:
        bp = ws["brand_profile"]
        bp.update(brand_name=req.brand_name, industry=req.industry,
                  description=req.description, website_url=req.website_url,
                  voice_summary=req.voice_summary, mission=req.mission,
                  updated_at=ts)
    else:
        bp = {
            "id": _rid("brand"),
            "workspace_id": workspace_id,
            "brand_name": req.brand_name,
            "industry": req.industry,
            "description": req.description,
            "website_url": req.website_url,
            "voice_summary": req.voice_summary,
            "mission": req.mission,
            "created_at": ts,
            "updated_at": ts,
        }
        ws["brand_profile"] = bp
    ws["brand_profile_id"] = bp["id"]
    return bp

# ── Audience Segments ───────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/audience-segments")
async def list_audience_segments(workspace_id: str):
    return _ensure_workspace(workspace_id)["audience_segments"]

@router.post("/workspaces/{workspace_id}/audience-segments", status_code=201)
async def create_audience_segment(workspace_id: str, req: AudienceSegmentRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    seg = {
        "id": _rid("seg"),
        "workspace_id": workspace_id,
        "name": req.name,
        "description": req.description,
        "age_range": req.age_range,
        "interests": req.interests,
        "primary_platform": req.primary_platform,
        "messaging_angle": req.messaging_angle,
        "created_at": ts,
        "updated_at": ts,
    }
    ws["audience_segments"].insert(0, seg)
    ws["audience_segment_count"] = len(ws["audience_segments"])
    return seg

@router.put("/workspaces/{workspace_id}/audience-segments/{segment_id}")
async def update_audience_segment(workspace_id: str, segment_id: str, req: AudienceSegmentRequest):
    ws = _ensure_workspace(workspace_id)
    for seg in ws["audience_segments"]:
        if seg["id"] == segment_id:
            seg.update(name=req.name, description=req.description,
                       age_range=req.age_range, interests=req.interests,
                       primary_platform=req.primary_platform,
                       messaging_angle=req.messaging_angle,
                       updated_at=_now())
            return seg
    raise HTTPException(status_code=404, detail="Segment not found")

@router.delete("/workspaces/{workspace_id}/audience-segments/{segment_id}", status_code=204)
async def delete_audience_segment(workspace_id: str, segment_id: str):
    ws = _ensure_workspace(workspace_id)
    ws["audience_segments"] = [s for s in ws["audience_segments"] if s["id"] != segment_id]
    ws["audience_segment_count"] = len(ws["audience_segments"])

# ── Strategies ──────────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/strategies")
async def list_strategies(workspace_id: str):
    return _ensure_workspace(workspace_id)["strategies"]

@router.get("/workspaces/{workspace_id}/strategies/latest")
async def get_latest_strategy(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    active = [s for s in ws["strategies"] if s.get("is_active")]
    if active:
        return active[0]
    if ws["strategies"]:
        return ws["strategies"][0]
    raise HTTPException(status_code=404, detail="No strategy found")

@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    for ws in _workspaces.values():
        for s in ws["strategies"]:
            if s["id"] == strategy_id:
                return s
    raise HTTPException(status_code=404, detail="Strategy not found")

@router.patch("/strategies/{strategy_id}/review")
async def review_strategy(strategy_id: str, req: ReviewStrategyRequest):
    for ws in _workspaces.values():
        for s in ws["strategies"]:
            if s["id"] == strategy_id:
                ts = _now()
                s["status"] = req.status
                s["review_notes"] = req.review_notes
                s["reviewed_at"] = ts
                s["updated_at"] = ts
                if req.status == "approved":
                    s["approved_at"] = ts
                _add_activity(ws, actor_label="Reviewer", entity_type="strategy",
                              entity_id=strategy_id, event_type="strategy_reviewed",
                              summary=f"Reviewed strategy v{s.get('version_number', 1)} as {req.status}.")
                if req.status == "approved":
                    _add_activity(ws, actor_label="Reviewer", entity_type="strategy",
                                  entity_id=strategy_id, event_type="approval_granted",
                                  summary=f"Approved strategy v{s.get('version_number', 1)} for planning.")
                return s
    raise HTTPException(status_code=404, detail="Strategy not found")

# ── Strategy Runs ───────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/strategy-runs", status_code=201)
async def start_strategy_run(workspace_id: str, req: StartStrategyRunRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    brand_name = ws["brand_profile"]["brand_name"] if ws["brand_profile"] else "Brand"

    # Deactivate current active strategy
    for s in ws["strategies"]:
        if s.get("is_active"):
            s["is_active"] = False
            s["superseded_at"] = ts

    current_version = max((s.get("version_number", 0) for s in ws["strategies"]), default=0)
    strategy_id = _rid("strategy")
    strategy = {
        "id": strategy_id,
        "workspace_id": workspace_id,
        "source_workflow_run_id": None,
        "parent_strategy_id": ws["strategies"][0]["id"] if ws["strategies"] else None,
        "version_number": current_version + 1,
        "is_active": True,
        "status": "in_review",
        "title": f"{brand_name} social media strategy v{current_version + 1}",
        "summary": f"AI-generated strategy for {brand_name} focused on {req.goal}.",
        "positioning_statement": f"{brand_name} helps its audience feel confident and informed.",
        "audience_focus": "Primary attention on the most engaged audience segments.",
        "channel_focus": "Lead with high-context formats, then repurpose into short-form content.",
        "campaign_note": f"Use the next cycle to prove the brand's point of view: {req.goal}",
        "review_notes": "Freshly generated — awaiting review.",
        "reviewed_by_member_id": None,
        "reviewed_at": None,
        "approved_at": None,
        "superseded_at": None,
        "platform_plans": [
            {"id": _rid("pp"), "brand_strategy_id": strategy_id, "platform_name": "Instagram",
             "objective": "Drive brand awareness and engagement.", "cadence_summary": "3 posts per week.",
             "content_mix": "Reels, carousels, and stories.", "success_signal": "Higher saves and shares.",
             "sort_order": 0, "created_at": ts, "updated_at": ts},
            {"id": _rid("pp"), "brand_strategy_id": strategy_id, "platform_name": "LinkedIn",
             "objective": "Build brand authority and partnerships.", "cadence_summary": "2 posts per week.",
             "content_mix": "Thought leadership and case studies.", "success_signal": "Comments from decision-makers.",
             "sort_order": 1, "created_at": ts, "updated_at": ts},
            {"id": _rid("pp"), "brand_strategy_id": strategy_id, "platform_name": "X",
             "objective": "Test hooks and build real-time engagement.", "cadence_summary": "3 posts per week.",
             "content_mix": "Punchy threads, hot takes, and community engagement.", "success_signal": "Retweets and replies.",
             "sort_order": 2, "created_at": ts, "updated_at": ts},
        ],
        "content_pillars": [
            {"id": _rid("pillar"), "brand_strategy_id": strategy_id, "name": "Brand clarity",
             "description": "Make the brand's point of view unmistakable.", "channel_angle": "Founder POV and process breakdowns.",
             "sort_order": 0, "created_at": ts, "updated_at": ts},
            {"id": _rid("pillar"), "brand_strategy_id": strategy_id, "name": "Social proof",
             "description": "Show results and community validation.", "channel_angle": "Testimonials, case studies, UGC.",
             "sort_order": 1, "created_at": ts, "updated_at": ts},
            {"id": _rid("pillar"), "brand_strategy_id": strategy_id, "name": "Engagement momentum",
             "description": "Keep the audience active and involved.", "channel_angle": "Polls, questions, behind-the-scenes.",
             "sort_order": 2, "created_at": ts, "updated_at": ts},
        ],
        "created_at": ts,
        "updated_at": ts,
    }
    ws["strategies"].insert(0, strategy)

    run_id = _rid("run")
    run = {
        "id": run_id,
        "workspace_id": workspace_id,
        "workflow_type": "strategy",
        "status": "completed",
        "input_payload": {"goal": req.goal},
        "output_payload": {"brand_strategy_id": strategy_id, "version_number": strategy["version_number"]},
        "error_message": None,
        "started_at": ts,
        "completed_at": ts,
        "initiated_by_member_id": req.initiated_by_member_id,
        "created_at": ts,
        "updated_at": ts,
    }
    strategy["source_workflow_run_id"] = run_id
    ws["workflow_runs"].insert(0, run)
    _add_activity(ws, actor_label="Workflow", entity_type="strategy", entity_id=strategy_id,
                  event_type="strategy_generated",
                  summary=f"Generated strategy v{strategy['version_number']}: {strategy['title']}.")
    return run

# ── Content Plans ───────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/content-plans")
async def list_content_plans(workspace_id: str):
    return _ensure_workspace(workspace_id)["content_plans"]

@router.get("/workspaces/{workspace_id}/content-plans/latest")
async def get_latest_content_plan(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    active = [p for p in ws["content_plans"] if p.get("is_active")]
    if active:
        return active[0]
    if ws["content_plans"]:
        return ws["content_plans"][0]
    raise HTTPException(status_code=404, detail="No content plan found")

@router.get("/content-plans/{plan_id}")
async def get_content_plan(plan_id: str):
    for ws in _workspaces.values():
        for p in ws["content_plans"]:
            if p["id"] == plan_id:
                return p
    raise HTTPException(status_code=404, detail="Content plan not found")

@router.post("/workspaces/{workspace_id}/content-plan-runs", status_code=201)
async def start_content_plan_run(workspace_id: str, req: StartContentPlanRunRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()

    strategy = None
    if req.brand_strategy_id:
        strategy = next((s for s in ws["strategies"] if s["id"] == req.brand_strategy_id), None)
    if not strategy:
        active = [s for s in ws["strategies"] if s.get("is_active")]
        strategy = active[0] if active else (ws["strategies"][0] if ws["strategies"] else None)
    if not strategy:
        raise HTTPException(status_code=400, detail="No strategy available. Generate a strategy first.")

    # Deactivate current
    for p in ws["content_plans"]:
        if p.get("is_active"):
            p["is_active"] = False
            p["superseded_at"] = ts

    current_version = max((p.get("version_number", 0) for p in ws["content_plans"]), default=0)
    plan_id = _rid("plan")
    pillars = [cp["name"] for cp in strategy.get("content_pillars", [])]
    platforms = [pp["platform_name"] for pp in strategy.get("platform_plans", [])]

    planned_posts = []
    formats = ["Reel", "Carousel", "Short video", "Founder POV", "Community prompt", "Thread"]
    for i in range(6):
        pp_id = _rid("post")
        platform = platforms[i % len(platforms)] if platforms else "Instagram"
        pillar_name = pillars[i % len(pillars)] if pillars else "General"
        pillar_id = strategy["content_pillars"][i % len(strategy["content_pillars"])]["id"] if strategy.get("content_pillars") else None
        post_date = (date.today() + timedelta(days=i + 1)).isoformat()
        planned_posts.append({
            "id": pp_id,
            "content_plan_id": plan_id,
            "workspace_id": workspace_id,
            "brand_strategy_id": strategy["id"],
            "content_pillar_id": pillar_id,
            "sequence_number": i + 1,
            "scheduled_for": post_date,
            "platform": platform,
            "format": formats[i % len(formats)],
            "title": f"{platform} {pillar_name} activation",
            "hook": f"Show how {pillar_name.lower()} creates visible brand momentum.",
            "angle": f"Use {strategy['title'].lower()} to make {pillar_name.lower()} feel actionable on {platform}.",
            "call_to_action": "Save, share, or reply with your take.",
            "status": "planned" if i == 0 else "in_review",
            "notes": f"Keep the tone grounded in {pillar_name.lower()}.",
            "approved_at": None,
            "publish_ready_at": None,
            "published_at": None,
            "created_at": ts,
            "updated_at": ts,
        })

    plan = {
        "id": plan_id,
        "workspace_id": workspace_id,
        "brand_strategy_id": strategy["id"],
        "source_workflow_run_id": None,
        "parent_plan_id": ws["content_plans"][0]["id"] if ws["content_plans"] else None,
        "version_number": current_version + 1,
        "is_active": True,
        "title": f"{strategy['title']} planning cycle",
        "planning_horizon_label": req.planning_horizon_label,
        "summary": f"A paced {req.planning_horizon_label.lower()} plan based on {strategy['title']}.",
        "status": "in_review",
        "review_notes": "Freshly generated.",
        "reviewed_by_member_id": None,
        "reviewed_at": None,
        "approved_at": None,
        "superseded_at": None,
        "planned_posts": planned_posts,
        "created_at": ts,
        "updated_at": ts,
    }
    ws["content_plans"].insert(0, plan)

    run_id = _rid("run")
    run = {
        "id": run_id,
        "workspace_id": workspace_id,
        "workflow_type": "content_plan",
        "status": "completed",
        "input_payload": {"brand_strategy_id": strategy["id"]},
        "output_payload": {"content_plan_id": plan_id, "planned_post_count": len(planned_posts)},
        "error_message": None,
        "started_at": ts,
        "completed_at": ts,
        "initiated_by_member_id": req.initiated_by_member_id,
        "created_at": ts,
        "updated_at": ts,
    }
    plan["source_workflow_run_id"] = run_id
    ws["workflow_runs"].insert(0, run)
    _add_activity(ws, actor_label="Workflow", entity_type="content_plan", entity_id=plan_id,
                  event_type="content_plan_generated",
                  summary=f"Generated content plan v{plan['version_number']}: {plan['title']}.")
    return run

# ── Planned Posts ────────────────────────────────────────────────────────────

@router.put("/planned-posts/{planned_post_id}")
async def update_planned_post(planned_post_id: str, req: UpdatePlannedPostRequest):
    for ws in _workspaces.values():
        for plan in ws["content_plans"]:
            for post in plan.get("planned_posts", []):
                if post["id"] == planned_post_id:
                    for field in ("scheduled_for", "platform", "format", "title",
                                  "hook", "angle", "call_to_action", "status", "notes"):
                        val = getattr(req, field, None)
                        if val is not None:
                            post[field] = val
                    post["updated_at"] = _now()
                    _add_activity(ws, actor_label="Operator", entity_type="planned_post",
                                  entity_id=planned_post_id, event_type="planned_post_edited",
                                  summary=f"Updated planned post '{post['title']}' to {post['status']}.")
                    return post
    raise HTTPException(status_code=404, detail="Planned post not found")

# ── Drafts ──────────────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/drafts")
async def list_drafts(workspace_id: str):
    return _ensure_workspace(workspace_id)["drafts"]

@router.get("/workspaces/{workspace_id}/drafts/review-queue")
async def list_review_queue(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    return [d for d in ws["drafts"] if d.get("review_status") in ("in_review", "draft", "changes_requested", "pending_review")]

@router.get("/workspaces/{workspace_id}/drafts/publishing-queue")
async def list_publishing_queue(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    return [d for d in ws["drafts"] if d.get("review_status") == "publish_ready"]

@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: str):
    for ws in _workspaces.values():
        for d in ws["drafts"]:
            if d["id"] == draft_id:
                return d
    raise HTTPException(status_code=404, detail="Draft not found")

@router.put("/drafts/{draft_id}")
async def update_draft(draft_id: str, req: UpdateDraftRequest):
    for ws in _workspaces.values():
        for d in ws["drafts"]:
            if d["id"] == draft_id:
                ts = _now()
                for field in ("title", "caption", "creative_brief", "call_to_action",
                              "hashtags", "review_status", "reviewer_notes", "scheduled_publish_at"):
                    val = getattr(req, field, None)
                    if val is not None:
                        d[field] = val
                d["reviewed_at"] = ts
                d["updated_at"] = ts
                if req.review_status == "approved":
                    d["approved_at"] = ts
                _add_activity(ws, actor_label="Reviewer", entity_type="post_draft",
                              entity_id=draft_id, event_type="review_status_changed",
                              summary=f"Updated draft '{d['title']}' to {d.get('review_status', 'unknown')}.")
                return d
    raise HTTPException(status_code=404, detail="Draft not found")

@router.post("/drafts/{draft_id}/publish-ready")
async def mark_publish_ready(draft_id: str, req: MarkPublishReadyRequest):
    for ws in _workspaces.values():
        for d in ws["drafts"]:
            if d["id"] == draft_id:
                ts = _now()
                d["review_status"] = "publish_ready"
                d["publish_ready_at"] = ts
                d["updated_at"] = ts
                if req.scheduled_publish_at:
                    d["scheduled_publish_at"] = req.scheduled_publish_at
                _add_activity(ws, actor_label="Reviewer", entity_type="post_draft",
                              entity_id=draft_id, event_type="publish_ready",
                              summary=f"Moved draft '{d['title']}' into the publish-ready queue.")
                return d
    raise HTTPException(status_code=404, detail="Draft not found")

@router.post("/drafts/{draft_id}/publish")
async def publish_draft(draft_id: str, req: PublishDraftRequest):
    for ws in _workspaces.values():
        for d in ws["drafts"]:
            if d["id"] == draft_id:
                ts = _now()
                d["review_status"] = "published"
                d["published_at"] = ts
                d["updated_at"] = ts
                d["mock_publishing_receipt"] = {
                    "receipt_id": _rid("receipt"),
                    "provider": "social_manager_backend",
                    "published_at": ts,
                }
                _add_activity(ws, actor_label="Publisher", entity_type="post_draft",
                              entity_id=draft_id, event_type="published",
                              summary=f"Published draft '{d['title']}'.")
                return d
    raise HTTPException(status_code=404, detail="Draft not found")

# ── Draft Runs ──────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/draft-runs", status_code=201)
async def start_draft_run(workspace_id: str, req: StartDraftRunRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()

    plan = None
    if req.content_plan_id:
        plan = next((p for p in ws["content_plans"] if p["id"] == req.content_plan_id), None)
    if not plan:
        active = [p for p in ws["content_plans"] if p.get("is_active")]
        plan = active[0] if active else (ws["content_plans"][0] if ws["content_plans"] else None)
    if not plan:
        raise HTTPException(status_code=400, detail="No content plan available. Generate a plan first.")

    generated = []
    for post in plan.get("planned_posts", []):
        draft = {
            "id": _rid("draft"),
            "workspace_id": workspace_id,
            "planned_post_id": post["id"],
            "source_workflow_run_id": None,
            "parent_draft_id": None,
            "version_number": 1,
            "is_current_version": True,
            "title": post["title"],
            "caption": f"{post['hook']}\n\n{post['angle']}\n\n{post['call_to_action']}",
            "creative_brief": f"Visualize {post['title'].lower()} with a premium, dark-shell product feel.",
            "call_to_action": post["call_to_action"],
            "hashtags": ["#SocialManager", f"#{post['platform'].replace(' ', '')}", f"#{post['format'].replace(' ', '')}"],
            "review_status": "in_review",
            "reviewer_notes": None,
            "reviewer_member_id": None,
            "reviewed_at": None,
            "approved_at": None,
            "publish_ready_at": None,
            "published_at": None,
            "scheduled_publish_at": None,
            "mock_publishing_receipt": None,
            "created_at": ts,
            "updated_at": ts,
        }
        generated.append(draft)

    run_id = _rid("run")
    run = {
        "id": run_id,
        "workspace_id": workspace_id,
        "workflow_type": "draft",
        "status": "completed",
        "input_payload": {"content_plan_id": plan["id"]},
        "output_payload": {"content_plan_id": plan["id"], "generated_count": len(generated)},
        "error_message": None,
        "started_at": ts,
        "completed_at": ts,
        "initiated_by_member_id": req.initiated_by_member_id,
        "created_at": ts,
        "updated_at": ts,
    }
    for d in generated:
        d["source_workflow_run_id"] = run_id

    ws["drafts"] = generated + ws["drafts"]
    ws["workflow_runs"].insert(0, run)
    for d in generated:
        _add_activity(ws, actor_label="Workflow", entity_type="post_draft",
                      entity_id=d["id"], event_type="draft_generated",
                      summary=f"Generated draft v1 for '{d['title']}'.")
    return run

# ── Workflow Runs ───────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/workflow-runs")
async def list_workflow_runs(workspace_id: str):
    return _ensure_workspace(workspace_id)["workflow_runs"]

@router.get("/workflow-runs/{run_id}")
async def get_workflow_run(run_id: str):
    for ws in _workspaces.values():
        for r in ws["workflow_runs"]:
            if r["id"] == run_id:
                return r
    raise HTTPException(status_code=404, detail="Workflow run not found")

# ── Activity ────────────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/activity")
async def list_activity(workspace_id: str, limit: int = Query(default=30, ge=1, le=100)):
    ws = _ensure_workspace(workspace_id)
    return ws["activity"][:limit]

@router.get("/workspaces/{workspace_id}/activity/summary")
async def get_activity_summary(workspace_id: str):
    ws = _ensure_workspace(workspace_id)
    events = ws["activity"]
    return {
        "total_events": len(events),
        "workflow_completions": sum(1 for e in events if e["event_type"] == "workflow_completed"),
        "approvals": sum(1 for e in events if e["event_type"] == "approval_granted"),
        "publish_ready_items": sum(1 for d in ws["drafts"] if d.get("review_status") == "publish_ready"),
        "latest_event_at": events[0]["created_at"] if events else None,
        "latest_summary": events[0]["summary"] if events else None,
    }

# ── Knowledge Base ──────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/knowledge-base/documents")
async def list_kb_documents(workspace_id: str):
    return _ensure_workspace(workspace_id)["knowledge_base_documents"]

@router.post("/workspaces/{workspace_id}/knowledge-base/documents", status_code=201)
async def upload_kb_document(workspace_id: str, req: UploadKBDocumentRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    doc = {
        "id": _rid("doc"),
        "workspace_id": workspace_id,
        "file_name": req.file_name,
        "category": req.category,
        "mime_type": req.mime_type,
        "size_bytes": req.size_bytes,
        "ingestion_status": "ready",
        "source": "upload",
        "uploaded_by_member_id": req.uploaded_by_member_id,
        "created_at": ts,
        "updated_at": ts,
    }
    ws["knowledge_base_documents"].insert(0, doc)
    _add_activity(ws, actor_label="Operator", entity_type="knowledge_document",
                  entity_id=doc["id"], event_type="document_uploaded",
                  summary=f"Uploaded knowledge document '{doc['file_name']}'.",
                  metadata_payload={"category": doc["category"], "size_bytes": doc["size_bytes"]})
    return doc

# ── Training Jobs ───────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/training-jobs")
async def list_training_jobs(workspace_id: str):
    return _ensure_workspace(workspace_id)["training_jobs"]

@router.post("/workspaces/{workspace_id}/training-jobs", status_code=201)
async def queue_training(workspace_id: str, req: QueueTrainingRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    job = {
        "id": _rid("training"),
        "workspace_id": workspace_id,
        "document_ids": req.document_ids,
        "category": req.category,
        "status": "completed",
        "created_at": ts,
        "updated_at": ts,
    }
    ws["training_jobs"].insert(0, job)
    _add_activity(ws, actor_label="Trainer", entity_type="training_job",
                  entity_id=job["id"], event_type="training_queued",
                  summary=f"Queued model training with {len(req.document_ids)} document(s).")
    return job

# ── Assistant Commands ──────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/assistant/commands")
async def assistant_command(workspace_id: str, req: AssistantCommandRequest):
    ws = _ensure_workspace(workspace_id)
    ts = _now()
    result = {
        "id": _rid("assistant"),
        "workspace_id": workspace_id,
        "route_context": req.route_context,
        "mode": req.mode,
        "prompt": req.prompt,
        "response": f"Logged '{req.prompt}' against {req.route_context}.",
        "created_at": ts,
    }
    _add_activity(ws, actor_label="Assistant", entity_type="assistant_command",
                  entity_id=result["id"], event_type="assistant_command_logged",
                  summary=f"Assistant command logged: {req.prompt[:80]}{'...' if len(req.prompt) > 80 else ''}")
    return result
