from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.content_plans.models import ContentPlan
    from app.modules.workflow_runs.models import WorkflowRun
    from app.modules.workspaces.models import Workspace


class StrategyStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class BrandStrategy(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "brand_strategies"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    source_workflow_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent_strategy_id: Mapped[str | None] = mapped_column(
        ForeignKey("brand_strategies.id", ondelete="SET NULL"),
        nullable=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[StrategyStatus] = mapped_column(
        Enum(StrategyStatus),
        default=StrategyStatus.DRAFT,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    positioning_statement: Mapped[str] = mapped_column(Text, nullable=False)
    audience_focus: Mapped[str] = mapped_column(Text, nullable=False)
    channel_focus: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="brand_strategies")
    source_workflow_run: Mapped["WorkflowRun | None"] = relationship()
    parent_strategy: Mapped["BrandStrategy | None"] = relationship(remote_side="BrandStrategy.id")
    platform_plans: Mapped[list["PlatformPlan"]] = relationship(
        back_populates="brand_strategy",
        cascade="all, delete-orphan",
        order_by="PlatformPlan.sort_order",
    )
    content_pillars: Mapped[list["ContentPillar"]] = relationship(
        back_populates="brand_strategy",
        cascade="all, delete-orphan",
        order_by="ContentPillar.sort_order",
    )
    content_plans: Mapped[list["ContentPlan"]] = relationship(
        back_populates="brand_strategy",
        cascade="all, delete-orphan",
    )


class PlatformPlan(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "platform_plans"

    brand_strategy_id: Mapped[str] = mapped_column(
        ForeignKey("brand_strategies.id", ondelete="CASCADE"),
        index=True,
    )
    platform_name: Mapped[str] = mapped_column(String(80), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    cadence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    content_mix: Mapped[str] = mapped_column(Text, nullable=False)
    success_signal: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    brand_strategy: Mapped["BrandStrategy"] = relationship(back_populates="platform_plans")


class ContentPillar(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "content_pillars"

    brand_strategy_id: Mapped[str] = mapped_column(
        ForeignKey("brand_strategies.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    channel_angle: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    brand_strategy: Mapped["BrandStrategy"] = relationship(back_populates="content_pillars")
