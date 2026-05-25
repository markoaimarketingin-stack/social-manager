from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.workspaces.models import Workspace


class WorkflowType(StrEnum):
    STRATEGY = "strategy"
    CONTENT_PLAN = "content_plan"
    DRAFT = "draft"


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowRun(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workflow_runs"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    workflow_type: Mapped[WorkflowType] = mapped_column(Enum(WorkflowType), nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus),
        default=WorkflowStatus.PENDING,
        nullable=False,
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    initiated_by_member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="workflow_runs")
