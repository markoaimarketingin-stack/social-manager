from fastapi import APIRouter

from app.modules.activity_events.router import router as activity_event_router
from app.modules.audience_segments.router import router as audience_segment_router
from app.modules.brand_strategies.router import router as brand_strategy_router
from app.modules.brand_profiles.router import router as brand_profile_router
from app.modules.content_plans.router import router as content_plan_router
from app.modules.post_drafts.router import router as post_draft_router
from app.modules.workflow_runs.router import router as workflow_run_router
from app.modules.workspaces.router import router as workspace_router

router = APIRouter()
router.include_router(workspace_router)
router.include_router(activity_event_router)
router.include_router(brand_profile_router)
router.include_router(audience_segment_router)
router.include_router(brand_strategy_router)
router.include_router(content_plan_router)
router.include_router(post_draft_router)
router.include_router(workflow_run_router)
