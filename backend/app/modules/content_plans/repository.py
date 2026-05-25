from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.content_plans.models import ContentPlan, PlannedPost


class ContentPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_workspace_id(self, workspace_id: str) -> list[ContentPlan]:
        result = await self.session.execute(
            select(ContentPlan)
            .options(selectinload(ContentPlan.planned_posts))
            .where(ContentPlan.workspace_id == workspace_id)
            .order_by(ContentPlan.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_workspace_id(self, workspace_id: str) -> ContentPlan | None:
        result = await self.session.execute(
            select(ContentPlan)
            .options(selectinload(ContentPlan.planned_posts))
            .where(ContentPlan.workspace_id == workspace_id)
            .order_by(ContentPlan.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active_by_workspace_id(self, workspace_id: str) -> ContentPlan | None:
        result = await self.session.execute(
            select(ContentPlan)
            .options(selectinload(ContentPlan.planned_posts))
            .where(ContentPlan.workspace_id == workspace_id, ContentPlan.is_active.is_(True))
            .order_by(ContentPlan.version_number.desc(), ContentPlan.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, content_plan_id: str) -> ContentPlan | None:
        result = await self.session.execute(
            select(ContentPlan)
            .options(selectinload(ContentPlan.planned_posts))
            .where(ContentPlan.id == content_plan_id)
        )
        return result.scalar_one_or_none()

    async def save(self, content_plan: ContentPlan) -> ContentPlan:
        self.session.add(content_plan)
        await self.session.flush()
        await self.session.refresh(content_plan)
        return content_plan

    async def get_next_version_number(self, workspace_id: str) -> int:
        result = await self.session.execute(
            select(func.max(ContentPlan.version_number)).where(ContentPlan.workspace_id == workspace_id)
        )
        current_max = result.scalar_one()
        return (current_max or 0) + 1


class PlannedPostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, planned_post_id: str) -> PlannedPost | None:
        result = await self.session.execute(select(PlannedPost).where(PlannedPost.id == planned_post_id))
        return result.scalar_one_or_none()

    async def list_by_content_plan_id(self, content_plan_id: str) -> list[PlannedPost]:
        result = await self.session.execute(
            select(PlannedPost)
            .where(PlannedPost.content_plan_id == content_plan_id)
            .order_by(PlannedPost.sequence_number.asc())
        )
        return list(result.scalars().all())

    async def list_by_workspace_id(self, workspace_id: str) -> list[PlannedPost]:
        result = await self.session.execute(
            select(PlannedPost)
            .where(PlannedPost.workspace_id == workspace_id)
            .order_by(PlannedPost.scheduled_for.asc(), PlannedPost.sequence_number.asc())
        )
        return list(result.scalars().all())

    async def save(self, planned_post: PlannedPost) -> PlannedPost:
        self.session.add(planned_post)
        await self.session.flush()
        await self.session.refresh(planned_post)
        return planned_post
