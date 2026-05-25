from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.audience_segments.models import AudienceSegment
from app.modules.audience_segments.repository import AudienceSegmentRepository
from app.modules.audience_segments.schemas import AudienceSegmentCreate, AudienceSegmentUpdate
from app.modules.workspaces.repository import WorkspaceRepository


class AudienceSegmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audience_segment_repository = AudienceSegmentRepository(session)
        self.workspace_repository = WorkspaceRepository(session)

    async def list_segments(self, workspace_id: str) -> list[AudienceSegment]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.audience_segment_repository.list_by_workspace_id(workspace_id)

    async def create_segment(
        self,
        workspace_id: str,
        payload: AudienceSegmentCreate,
    ) -> AudienceSegment:
        await self._ensure_workspace_exists(workspace_id)
        segment = AudienceSegment(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description,
            age_range=payload.age_range,
            interests=payload.interests,
            primary_platform=payload.primary_platform,
            messaging_angle=payload.messaging_angle,
        )
        await self.audience_segment_repository.save(segment)
        await self.session.commit()
        return segment

    async def update_segment(
        self,
        workspace_id: str,
        segment_id: str,
        payload: AudienceSegmentUpdate,
    ) -> AudienceSegment:
        segment = await self.audience_segment_repository.get_by_id(workspace_id, segment_id)
        if segment is None:
            raise NotFoundError("Audience segment not found", code="audience_segment_not_found")

        segment.name = payload.name
        segment.description = payload.description
        segment.age_range = payload.age_range
        segment.interests = payload.interests
        segment.primary_platform = payload.primary_platform
        segment.messaging_angle = payload.messaging_angle

        await self.audience_segment_repository.save(segment)
        await self.session.commit()
        return segment

    async def delete_segment(self, workspace_id: str, segment_id: str) -> None:
        segment = await self.audience_segment_repository.get_by_id(workspace_id, segment_id)
        if segment is None:
            raise NotFoundError("Audience segment not found", code="audience_segment_not_found")

        await self.audience_segment_repository.delete(segment)
        await self.session.commit()

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
