from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.content_plans.schemas import ContentPlanResponse, PlannedPostResponse, PlannedPostUpdate
from app.modules.content_plans.service import ContentPlanService

router = APIRouter(tags=["content_plans"])


@router.get("/workspaces/{workspace_id}/content-plans", response_model=list[ContentPlanResponse])
async def list_content_plans(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[ContentPlanResponse]:
    service = ContentPlanService(session)
    plans = await service.list_plans(workspace_id)
    return [ContentPlanResponse.model_validate(plan) for plan in plans]


@router.get("/workspaces/{workspace_id}/content-plans/latest", response_model=ContentPlanResponse)
async def get_latest_content_plan(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> ContentPlanResponse:
    service = ContentPlanService(session)
    plan = await service.get_latest_plan(workspace_id)
    return ContentPlanResponse.model_validate(plan)


@router.get("/content-plans/{content_plan_id}", response_model=ContentPlanResponse)
async def get_content_plan(
    content_plan_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> ContentPlanResponse:
    service = ContentPlanService(session)
    plan = await service.get_plan(content_plan_id)
    return ContentPlanResponse.model_validate(plan)


@router.put("/planned-posts/{planned_post_id}", response_model=PlannedPostResponse)
async def update_planned_post(
    planned_post_id: str,
    payload: PlannedPostUpdate,
    session: AsyncSession = Depends(db_session_dependency),
) -> PlannedPostResponse:
    service = ContentPlanService(session)
    planned_post = await service.update_planned_post(planned_post_id, payload)
    return PlannedPostResponse.model_validate(planned_post)
