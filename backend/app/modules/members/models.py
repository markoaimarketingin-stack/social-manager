from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.workspaces.models import Workspace


class MemberRole(StrEnum):
    OWNER = "owner"
    MANAGER = "manager"


class Member(Base, UuidPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "members"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole), default=MemberRole.OWNER, nullable=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="members")
