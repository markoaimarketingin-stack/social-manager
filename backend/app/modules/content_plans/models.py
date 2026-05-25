from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.brand_strategies.models import BrandStrategy, ContentPillar
    from app.modules.post_drafts.models import PostDraft
    from app.modules.workflow_runs.models import WorkflowRun
    from app.modules.workspaces.models import Workspace


class ContentPlanStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    READY = "ready"


class PlannedPostStatus(StrEnum):
    PLANNED = "planned"
    DRAFTED = "drafted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISH_READY = "publish_ready"
    PUBLISHED = "published"
    REJECTED = "rejected"
    READY_FOR_REVIEW = "ready_for_review"


class ContentPlan(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "content_plans"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    brand_strategy_id: Mapped[str] = mapped_column(
        ForeignKey("brand_strategies.id", ondelete="CASCADE"),
        index=True,
    )
    source_workflow_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent_plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("content_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    planning_horizon_label: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ContentPlanStatus] = mapped_column(
        Enum(ContentPlanStatus),
        default=ContentPlanStatus.DRAFT,
        nullable=False,
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="content_plans")
    brand_strategy: Mapped["BrandStrategy"] = relationship(back_populates="content_plans")
    source_workflow_run: Mapped["WorkflowRun | None"] = relationship()
    parent_plan: Mapped["ContentPlan | None"] = relationship(remote_side="ContentPlan.id")
    planned_posts: Mapped[list["PlannedPost"]] = relationship(
        back_populates="content_plan",
        cascade="all, delete-orphan",
        order_by="PlannedPost.sequence_number",
    )


class PlannedPost(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "planned_posts"

    content_plan_id: Mapped[str] = mapped_column(ForeignKey("content_plans.id", ondelete="CASCADE"), index=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    brand_strategy_id: Mapped[str] = mapped_column(
        ForeignKey("brand_strategies.id", ondelete="CASCADE"),
        index=True,
    )
    content_pillar_id: Mapped[str | None] = mapped_column(
        ForeignKey("content_pillars.id", ondelete="SET NULL"),
        nullable=True,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False)
    platform: Mapped[str] = mapped_column(String(80), nullable=False)
    format: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(Text, nullable=False)
    call_to_action: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PlannedPostStatus] = mapped_column(
        Enum(PlannedPostStatus),
        default=PlannedPostStatus.PLANNED,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    publish_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    content_plan: Mapped["ContentPlan"] = relationship(back_populates="planned_posts")
    content_pillar: Mapped["ContentPillar | None"] = relationship()
    drafts: Mapped[list["PostDraft"]] = relationship(
        back_populates="planned_post",
        cascade="all, delete-orphan",
        order_by="PostDraft.version_number.desc()",
    )
