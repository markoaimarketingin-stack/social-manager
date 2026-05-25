from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.workspaces.schemas import WorkspaceCreate, WorkspaceDetailResponse, WorkspaceResponse
from app.modules.workspaces.service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    payload: WorkspaceCreate,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkspaceResponse:
    service = WorkspaceService(session)
    workspace = await service.create_workspace(payload)
    return WorkspaceResponse.model_validate(workspace)


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> WorkspaceDetailResponse:
    service = WorkspaceService(session)
    workspace = await service.get_workspace(workspace_id)
    return WorkspaceDetailResponse(
        **WorkspaceResponse.model_validate(workspace).model_dump(),
        brand_profile_id=workspace.brand_profile.id if workspace.brand_profile is not None else None,
        member_count=len(workspace.members),
        audience_segment_count=len(workspace.audience_segments),
    )
