from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.post_drafts.models import DraftReviewStatus


class PostDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    planned_post_id: str
    source_workflow_run_id: str | None
    parent_draft_id: str | None
    version_number: int
    is_current_version: bool
    title: str
    caption: str
    creative_brief: str
    call_to_action: str
    hashtags: list[str]
    review_status: DraftReviewStatus
    reviewer_notes: str | None
    reviewer_member_id: str | None
    reviewed_at: datetime | None
    approved_at: datetime | None
    publish_ready_at: datetime | None
    published_at: datetime | None
    scheduled_publish_at: datetime | None
    mock_publishing_receipt: dict[str, object] | None
    created_at: datetime
    updated_at: datetime


class DraftGenerateRequest(BaseModel):
    content_plan_id: str | None = None
    initiated_by_member_id: str | None = None


class PostDraftUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    caption: str = Field(min_length=2, max_length=4000)
    creative_brief: str = Field(min_length=2, max_length=2000)
    call_to_action: str = Field(min_length=2, max_length=600)
    hashtags: list[str] = Field(default_factory=list, max_length=15)
    review_status: DraftReviewStatus = DraftReviewStatus.IN_REVIEW
    reviewer_notes: str | None = Field(default=None, max_length=2000)
    reviewer_member_id: str | None = Field(default=None, max_length=36)
    scheduled_publish_at: datetime | None = None


class DraftPublishReadyRequest(BaseModel):
    reviewer_member_id: str | None = Field(default=None, max_length=36)
    scheduled_publish_at: datetime | None = None


class DraftPublishRequest(BaseModel):
    reviewer_member_id: str | None = Field(default=None, max_length=36)
