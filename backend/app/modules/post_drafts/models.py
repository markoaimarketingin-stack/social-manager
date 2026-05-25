from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.content_plans.models import PlannedPost
    from app.modules.workflow_runs.models import WorkflowRun
    from app.modules.workspaces.models import Workspace


class DraftReviewStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISH_READY = "publish_ready"
    PUBLISHED = "published"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class PostDraft(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "post_drafts"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    planned_post_id: Mapped[str] = mapped_column(
        ForeignKey("planned_posts.id", ondelete="CASCADE"),
        index=True,
    )
    source_workflow_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent_draft_id: Mapped[str | None] = mapped_column(
        ForeignKey("post_drafts.id", ondelete="SET NULL"),
        nullable=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_current_version: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    creative_brief: Mapped[str] = mapped_column(Text, nullable=False)
    call_to_action: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    review_status: Mapped[DraftReviewStatus] = mapped_column(
        Enum(DraftReviewStatus),
        default=DraftReviewStatus.IN_REVIEW,
        nullable=False,
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    publish_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_publish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mock_publishing_receipt: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="post_drafts")
    planned_post: Mapped["PlannedPost"] = relationship(back_populates="drafts")
    source_workflow_run: Mapped["WorkflowRun | None"] = relationship()
    parent_draft: Mapped["PostDraft | None"] = relationship(remote_side="PostDraft.id")
