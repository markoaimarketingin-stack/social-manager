from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.activity_events.schemas import (
    WorkspaceActivityEventResponse,
    WorkspaceActivitySummaryResponse,
)
from app.modules.activity_events.service import WorkspaceActivityEventService

router = APIRouter(tags=["activity_events"])


@router.get("/workspaces/{workspace_id}/activity", response_model=list[WorkspaceActivityEventResponse])
async def list_workspace_activity(
    workspace_id: str,
    limit: int = Query(default=30, ge=1, le=100),
    session: AsyncSession = Depends(db_session_dependency),
) -> list[WorkspaceActivityEventResponse]:
    service = WorkspaceActivityEventService(session)
    events = await service.list_events(workspace_id, limit=limit)
    return [WorkspaceActivityEventResponse.model_validate(event) for event in events]


@router.get("/workspaces/{workspace_id}/activity/summary", response_model=WorkspaceActivitySummaryResponse)
async def get_workspace_activity_summary(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkspaceActivitySummaryResponse:
    service = WorkspaceActivityEventService(session)
    return await service.get_summary(workspace_id)
