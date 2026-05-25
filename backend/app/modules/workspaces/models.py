from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.activity_events.models import WorkspaceActivityEvent
    from app.modules.audience_segments.models import AudienceSegment
    from app.modules.brand_strategies.models import BrandStrategy
    from app.modules.brand_profiles.models import BrandProfile
    from app.modules.content_plans.models import ContentPlan
    from app.modules.members.models import Member
    from app.modules.post_drafts.models import PostDraft
    from app.modules.workflow_runs.models import WorkflowRun


class Workspace(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)

    members: Mapped[list["Member"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    brand_profile: Mapped["BrandProfile | None"] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        uselist=False,
    )
    audience_segments: Mapped[list["AudienceSegment"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    brand_strategies: Mapped[list["BrandStrategy"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    content_plans: Mapped[list["ContentPlan"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    post_drafts: Mapped[list["PostDraft"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    workflow_runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    activity_events: Mapped[list["WorkspaceActivityEvent"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        order_by="WorkspaceActivityEvent.created_at.desc()",
    )
