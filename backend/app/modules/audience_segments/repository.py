from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audience_segments.models import AudienceSegment


class AudienceSegmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_workspace_id(self, workspace_id: str) -> list[AudienceSegment]:
        result = await self.session.execute(
            select(AudienceSegment)
            .where(AudienceSegment.workspace_id == workspace_id)
            .order_by(AudienceSegment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, workspace_id: str, segment_id: str) -> AudienceSegment | None:
        result = await self.session.execute(
            select(AudienceSegment).where(
                AudienceSegment.workspace_id == workspace_id,
                AudienceSegment.id == segment_id,
            )
        )
        return result.scalar_one_or_none()

    async def save(self, audience_segment: AudienceSegment) -> AudienceSegment:
        self.session.add(audience_segment)
        await self.session.flush()
        await self.session.refresh(audience_segment)
        return audience_segment

    async def delete(self, audience_segment: AudienceSegment) -> None:
        await self.session.delete(audience_segment)
