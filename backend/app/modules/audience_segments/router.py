from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.audience_segments.schemas import (
    AudienceSegmentCreate,
    AudienceSegmentResponse,
    AudienceSegmentUpdate,
)
from app.modules.audience_segments.service import AudienceSegmentService

router = APIRouter(prefix="/workspaces/{workspace_id}/audience-segments", tags=["audience_segments"])


@router.get("", response_model=list[AudienceSegmentResponse])
async def list_audience_segments(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[AudienceSegmentResponse]:
    service = AudienceSegmentService(session)
    segments = await service.list_segments(workspace_id)
    return [AudienceSegmentResponse.model_validate(segment) for segment in segments]


@router.post("", response_model=AudienceSegmentResponse, status_code=201)
async def create_audience_segment(
    workspace_id: str,
    payload: AudienceSegmentCreate,
    session: AsyncSession = Depends(db_session_dependency),
) -> AudienceSegmentResponse:
    service = AudienceSegmentService(session)
    segment = await service.create_segment(workspace_id, payload)
    return AudienceSegmentResponse.model_validate(segment)


@router.put("/{segment_id}", response_model=AudienceSegmentResponse)
async def update_audience_segment(
    workspace_id: str,
    segment_id: str,
    payload: AudienceSegmentUpdate,
    session: AsyncSession = Depends(db_session_dependency),
) -> AudienceSegmentResponse:
    service = AudienceSegmentService(session)
    segment = await service.update_segment(workspace_id, segment_id, payload)
    return AudienceSegmentResponse.model_validate(segment)


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audience_segment(
    workspace_id: str,
    segment_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> Response:
    service = AudienceSegmentService(session)
    await service.delete_segment(workspace_id, segment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
