from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import WorkspaceActivityEventService
from app.modules.content_plans.models import PlannedPostStatus
from app.modules.content_plans.repository import PlannedPostRepository
from app.modules.post_drafts.models import DraftReviewStatus, PostDraft
from app.modules.post_drafts.repository import PostDraftRepository
from app.modules.post_drafts.schemas import DraftPublishReadyRequest, DraftPublishRequest, PostDraftUpdate
from app.modules.workspaces.repository import WorkspaceRepository


class PostDraftService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.post_draft_repository = PostDraftRepository(session)
        self.planned_post_repository = PlannedPostRepository(session)
        self.workspace_repository = WorkspaceRepository(session)
        self.activity_service = WorkspaceActivityEventService(session)

    async def list_drafts(self, workspace_id: str) -> list[PostDraft]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.post_draft_repository.list_by_workspace_id(workspace_id)

    async def list_review_queue(self, workspace_id: str) -> list[PostDraft]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.post_draft_repository.list_review_queue(workspace_id)

    async def list_publish_ready_queue(self, workspace_id: str) -> list[PostDraft]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.post_draft_repository.list_publish_ready_queue(workspace_id)

    async def get_draft(self, draft_id: str) -> PostDraft:
        draft = await self.post_draft_repository.get_by_id(draft_id)
        if draft is None:
            raise NotFoundError("Draft not found", code="draft_not_found")
        return draft

    async def update_draft(self, draft_id: str, payload: PostDraftUpdate) -> PostDraft:
        draft = await self.get_draft(draft_id)
        draft.title = payload.title
        draft.caption = payload.caption
        draft.creative_brief = payload.creative_brief
        draft.call_to_action = payload.call_to_action
        draft.hashtags = payload.hashtags
        draft.review_status = payload.review_status
        draft.reviewer_notes = payload.reviewer_notes
        draft.reviewer_member_id = payload.reviewer_member_id
        draft.scheduled_publish_at = payload.scheduled_publish_at
        draft.reviewed_at = datetime.now(timezone.utc)
        if payload.review_status == DraftReviewStatus.APPROVED:
            draft.approved_at = datetime.now(timezone.utc)

        planned_post = await self.planned_post_repository.get_by_id(draft.planned_post_id)
        if planned_post is not None:
            planned_post.status = self._planned_post_status_for_draft_status(payload.review_status)
            if payload.review_status == DraftReviewStatus.APPROVED:
                planned_post.approved_at = datetime.now(timezone.utc)

        await self.post_draft_repository.save(draft)
        await self.activity_service.record_event(
            workspace_id=draft.workspace_id,
            entity_type=ActivityEntityType.POST_DRAFT,
            entity_id=draft.id,
            event_type=ActivityEventType.REVIEW_STATUS_CHANGED,
            summary=f"Updated draft '{draft.title}' to {payload.review_status.value}.",
            actor_member_id=payload.reviewer_member_id,
            actor_label="Reviewer",
            metadata_payload={
                "planned_post_id": draft.planned_post_id,
                "status": payload.review_status.value,
            },
        )
        if payload.review_status == DraftReviewStatus.APPROVED:
            await self.activity_service.record_event(
                workspace_id=draft.workspace_id,
                entity_type=ActivityEntityType.POST_DRAFT,
                entity_id=draft.id,
                event_type=ActivityEventType.APPROVAL_GRANTED,
                summary=f"Approved draft '{draft.title}' for publishing prep.",
                actor_member_id=payload.reviewer_member_id,
                actor_label="Reviewer",
                metadata_payload={"planned_post_id": draft.planned_post_id},
            )
        await self.session.commit()
        return draft

    async def mark_publish_ready(
        self,
        draft_id: str,
        payload: DraftPublishReadyRequest,
    ) -> PostDraft:
        draft = await self.get_draft(draft_id)
        draft.review_status = DraftReviewStatus.PUBLISH_READY
        draft.reviewer_member_id = payload.reviewer_member_id
        draft.reviewed_at = datetime.now(timezone.utc)
        draft.publish_ready_at = datetime.now(timezone.utc)
        draft.scheduled_publish_at = payload.scheduled_publish_at

        planned_post = await self.planned_post_repository.get_by_id(draft.planned_post_id)
        if planned_post is not None:
            planned_post.status = PlannedPostStatus.PUBLISH_READY
            planned_post.publish_ready_at = draft.publish_ready_at

        await self.post_draft_repository.save(draft)
        await self.activity_service.record_event(
            workspace_id=draft.workspace_id,
            entity_type=ActivityEntityType.POST_DRAFT,
            entity_id=draft.id,
            event_type=ActivityEventType.PUBLISH_READY,
            summary=f"Moved draft '{draft.title}' into the publish-ready queue.",
            actor_member_id=payload.reviewer_member_id,
            actor_label="Reviewer",
            metadata_payload={"scheduled_publish_at": draft.scheduled_publish_at.isoformat() if draft.scheduled_publish_at else None},
        )
        await self.session.commit()
        return draft

    async def publish_draft(self, draft_id: str, payload: DraftPublishRequest) -> PostDraft:
        draft = await self.get_draft(draft_id)
        draft.review_status = DraftReviewStatus.PUBLISHED
        draft.reviewer_member_id = payload.reviewer_member_id
        draft.reviewed_at = datetime.now(timezone.utc)
        draft.published_at = datetime.now(timezone.utc)
        draft.mock_publishing_receipt = {
            "receipt_id": f"mock-publish-{uuid4().hex[:10]}",
            "published_at": draft.published_at.isoformat(),
            "scheduled_publish_at": draft.scheduled_publish_at.isoformat()
            if draft.scheduled_publish_at
            else None,
            "provider": "mock_publisher",
        }

        planned_post = await self.planned_post_repository.get_by_id(draft.planned_post_id)
        if planned_post is not None:
            planned_post.status = PlannedPostStatus.PUBLISHED
            planned_post.published_at = draft.published_at

        await self.post_draft_repository.save(draft)
        await self.activity_service.record_event(
            workspace_id=draft.workspace_id,
            entity_type=ActivityEntityType.POST_DRAFT,
            entity_id=draft.id,
            event_type=ActivityEventType.PUBLISHED,
            summary=f"Published draft '{draft.title}' with a mock receipt.",
            actor_member_id=payload.reviewer_member_id,
            actor_label="Publisher",
            metadata_payload=draft.mock_publishing_receipt,
        )
        await self.session.commit()
        return draft

    @staticmethod
    def _planned_post_status_for_draft_status(status: DraftReviewStatus) -> PlannedPostStatus:
        mapping = {
            DraftReviewStatus.DRAFT: PlannedPostStatus.DRAFTED,
            DraftReviewStatus.IN_REVIEW: PlannedPostStatus.IN_REVIEW,
            DraftReviewStatus.PENDING_REVIEW: PlannedPostStatus.IN_REVIEW,
            DraftReviewStatus.APPROVED: PlannedPostStatus.APPROVED,
            DraftReviewStatus.PUBLISH_READY: PlannedPostStatus.PUBLISH_READY,
            DraftReviewStatus.PUBLISHED: PlannedPostStatus.PUBLISHED,
            DraftReviewStatus.REJECTED: PlannedPostStatus.REJECTED,
            DraftReviewStatus.CHANGES_REQUESTED: PlannedPostStatus.IN_REVIEW,
        }
        return mapping[status]

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
