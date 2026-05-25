from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.post_drafts.models import DraftReviewStatus, PostDraft


class PostDraftRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_workspace_id(self, workspace_id: str) -> list[PostDraft]:
        result = await self.session.execute(
            select(PostDraft)
            .options(selectinload(PostDraft.planned_post))
            .where(PostDraft.workspace_id == workspace_id)
            .order_by(PostDraft.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_review_queue(self, workspace_id: str) -> list[PostDraft]:
        result = await self.session.execute(
            select(PostDraft)
            .options(selectinload(PostDraft.planned_post))
            .where(
                PostDraft.workspace_id == workspace_id,
                PostDraft.review_status.in_(
                    [
                        DraftReviewStatus.IN_REVIEW,
                        DraftReviewStatus.PENDING_REVIEW,
                        DraftReviewStatus.CHANGES_REQUESTED,
                    ]
                ),
            )
            .order_by(PostDraft.updated_at.desc())
        )
        return list(result.scalars().all())

    async def list_publish_ready_queue(self, workspace_id: str) -> list[PostDraft]:
        result = await self.session.execute(
            select(PostDraft)
            .options(selectinload(PostDraft.planned_post))
            .where(
                PostDraft.workspace_id == workspace_id,
                PostDraft.review_status == DraftReviewStatus.PUBLISH_READY,
            )
            .order_by(PostDraft.scheduled_publish_at.asc().nullslast(), PostDraft.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, draft_id: str) -> PostDraft | None:
        result = await self.session.execute(
            select(PostDraft)
            .options(selectinload(PostDraft.planned_post))
            .where(PostDraft.id == draft_id)
        )
        return result.scalar_one_or_none()

    async def get_next_version_number(self, planned_post_id: str) -> int:
        result = await self.session.execute(
            select(func.max(PostDraft.version_number)).where(PostDraft.planned_post_id == planned_post_id)
        )
        current_max = result.scalar_one()
        return (current_max or 0) + 1

    async def get_current_by_planned_post_id(self, planned_post_id: str) -> PostDraft | None:
        result = await self.session.execute(
            select(PostDraft)
            .where(PostDraft.planned_post_id == planned_post_id, PostDraft.is_current_version.is_(True))
            .order_by(PostDraft.version_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save(self, draft: PostDraft) -> PostDraft:
        self.session.add(draft)
        await self.session.flush()
        await self.session.refresh(draft)
        return draft
