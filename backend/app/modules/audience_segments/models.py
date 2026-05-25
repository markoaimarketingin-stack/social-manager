from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.workspaces.models import Workspace


class AudienceSegment(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audience_segments"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(80), nullable=True)
    interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    primary_platform: Mapped[str | None] = mapped_column(String(80), nullable=True)
    messaging_angle: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="audience_segments")
