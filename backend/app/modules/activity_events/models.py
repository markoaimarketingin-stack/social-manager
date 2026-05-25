from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.workspaces.models import Workspace


class ActivityEntityType(StrEnum):
    WORKSPACE = "workspace"
    STRATEGY = "strategy"
    CONTENT_PLAN = "content_plan"
    PLANNED_POST = "planned_post"
    POST_DRAFT = "post_draft"
    WORKFLOW_RUN = "workflow_run"


class ActivityEventType(StrEnum):
    WORKSPACE_CREATED = "workspace_created"
    STRATEGY_GENERATED = "strategy_generated"
    STRATEGY_REVIEWED = "strategy_reviewed"
    CONTENT_PLAN_GENERATED = "content_plan_generated"
    PLANNED_POST_EDITED = "planned_post_edited"
    DRAFT_GENERATED = "draft_generated"
    DRAFT_UPDATED = "draft_updated"
    REVIEW_STATUS_CHANGED = "review_status_changed"
    APPROVAL_GRANTED = "approval_granted"
    PUBLISH_READY = "publish_ready"
    PUBLISHED = "published"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


class WorkspaceActivityEvent(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workspace_activity_events"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    actor_member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    actor_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entity_type: Mapped[ActivityEntityType] = mapped_column(Enum(ActivityEntityType), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    event_type: Mapped[ActivityEventType] = mapped_column(Enum(ActivityEventType), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="activity_events")
