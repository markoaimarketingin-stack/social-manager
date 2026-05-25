from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import WorkspaceActivityEventService
from app.modules.content_plans.models import ContentPlan, PlannedPost, PlannedPostStatus
from app.modules.content_plans.repository import ContentPlanRepository, PlannedPostRepository
from app.modules.content_plans.schemas import PlannedPostUpdate
from app.modules.workspaces.repository import WorkspaceRepository


class ContentPlanService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.content_plan_repository = ContentPlanRepository(session)
        self.planned_post_repository = PlannedPostRepository(session)
        self.workspace_repository = WorkspaceRepository(session)
        self.activity_service = WorkspaceActivityEventService(session)

    async def list_plans(self, workspace_id: str) -> list[ContentPlan]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.content_plan_repository.list_by_workspace_id(workspace_id)

    async def get_latest_plan(self, workspace_id: str) -> ContentPlan:
        await self._ensure_workspace_exists(workspace_id)
        content_plan = await self.content_plan_repository.get_active_by_workspace_id(workspace_id)
        if content_plan is None:
            content_plan = await self.content_plan_repository.get_latest_by_workspace_id(workspace_id)
        if content_plan is None:
            raise NotFoundError("Content plan not found", code="content_plan_not_found")
        return content_plan

    async def get_plan(self, content_plan_id: str) -> ContentPlan:
        content_plan = await self.content_plan_repository.get_by_id(content_plan_id)
        if content_plan is None:
            raise NotFoundError("Content plan not found", code="content_plan_not_found")
        return content_plan

    async def update_planned_post(self, planned_post_id: str, payload: PlannedPostUpdate) -> PlannedPost:
        planned_post = await self.planned_post_repository.get_by_id(planned_post_id)
        if planned_post is None:
            raise NotFoundError("Planned post not found", code="planned_post_not_found")

        planned_post.scheduled_for = payload.scheduled_for
        planned_post.platform = payload.platform
        planned_post.format = payload.format
        planned_post.title = payload.title
        planned_post.hook = payload.hook
        planned_post.angle = payload.angle
        planned_post.call_to_action = payload.call_to_action
        planned_post.status = payload.status
        planned_post.notes = payload.notes
        if payload.status == PlannedPostStatus.APPROVED:
            planned_post.approved_at = datetime.now(timezone.utc)
        if payload.status == PlannedPostStatus.PUBLISH_READY:
            planned_post.publish_ready_at = datetime.now(timezone.utc)
        if payload.status == PlannedPostStatus.PUBLISHED:
            planned_post.published_at = datetime.now(timezone.utc)

        await self.planned_post_repository.save(planned_post)
        await self.activity_service.record_event(
            workspace_id=planned_post.workspace_id,
            entity_type=ActivityEntityType.PLANNED_POST,
            entity_id=planned_post.id,
            event_type=ActivityEventType.PLANNED_POST_EDITED,
            summary=f"Updated planned post '{planned_post.title}' to {payload.status.value}.",
            actor_member_id=payload.reviewer_member_id,
            actor_label="Operator",
            metadata_payload={
                "content_plan_id": planned_post.content_plan_id,
                "status": payload.status.value,
            },
        )
        await self.session.commit()
        return planned_post

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
