from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType, WorkspaceActivityEvent
from app.modules.activity_events.repository import WorkspaceActivityEventRepository
from app.modules.activity_events.schemas import WorkspaceActivitySummaryResponse
from app.modules.workspaces.repository import WorkspaceRepository


class WorkspaceActivityEventService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = WorkspaceActivityEventRepository(session)
        self.workspace_repository = WorkspaceRepository(session)

    async def list_events(self, workspace_id: str, limit: int = 40) -> list[WorkspaceActivityEvent]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.repository.list_by_workspace_id(workspace_id, limit=limit)

    async def get_summary(self, workspace_id: str) -> WorkspaceActivitySummaryResponse:
        await self._ensure_workspace_exists(workspace_id)
        events = await self.repository.list_by_workspace_id(workspace_id, limit=1)
        return WorkspaceActivitySummaryResponse(
            total_events=await self.repository.count_by_workspace_id(workspace_id),
            workflow_completions=await self.repository.count_by_event_type(
                workspace_id, ActivityEventType.WORKFLOW_COMPLETED
            ),
            approvals=await self.repository.count_by_event_type(
                workspace_id, ActivityEventType.APPROVAL_GRANTED
            ),
            publish_ready_items=await self.repository.count_by_event_type(
                workspace_id, ActivityEventType.PUBLISH_READY
            ),
            latest_event_at=events[0].created_at if events else None,
            latest_summary=events[0].summary if events else None,
        )

    async def record_event(
        self,
        *,
        workspace_id: str,
        entity_type: ActivityEntityType,
        entity_id: str | None,
        event_type: ActivityEventType,
        summary: str,
        actor_member_id: str | None = None,
        actor_label: str | None = None,
        metadata_payload: dict[str, Any] | None = None,
    ) -> WorkspaceActivityEvent:
        event = WorkspaceActivityEvent(
            workspace_id=workspace_id,
            actor_member_id=actor_member_id,
            actor_label=actor_label,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            summary=summary,
            metadata_payload=metadata_payload or {},
        )
        return await self.repository.save(event)

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
