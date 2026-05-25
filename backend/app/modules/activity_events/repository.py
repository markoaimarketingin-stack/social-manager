from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.activity_events.models import ActivityEventType, WorkspaceActivityEvent


class WorkspaceActivityEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_workspace_id(self, workspace_id: str, limit: int = 40) -> list[WorkspaceActivityEvent]:
        result = await self.session.execute(
            select(WorkspaceActivityEvent)
            .where(WorkspaceActivityEvent.workspace_id == workspace_id)
            .order_by(WorkspaceActivityEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_workspace_id(self, workspace_id: str) -> int:
        result = await self.session.execute(
            select(func.count(WorkspaceActivityEvent.id)).where(
                WorkspaceActivityEvent.workspace_id == workspace_id
            )
        )
        return int(result.scalar_one() or 0)

    async def count_by_event_type(self, workspace_id: str, event_type: ActivityEventType) -> int:
        result = await self.session.execute(
            select(func.count(WorkspaceActivityEvent.id)).where(
                WorkspaceActivityEvent.workspace_id == workspace_id,
                WorkspaceActivityEvent.event_type == event_type,
            )
        )
        return int(result.scalar_one() or 0)

    async def save(self, event: WorkspaceActivityEvent) -> WorkspaceActivityEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event
