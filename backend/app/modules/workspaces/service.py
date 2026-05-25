from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import WorkspaceActivityEventService
from app.modules.brand_profiles.repository import BrandProfileRepository
from app.modules.members.models import Member, MemberRole
from app.modules.workspaces.models import Workspace
from app.modules.workspaces.repository import WorkspaceRepository
from app.modules.workspaces.schemas import WorkspaceCreate


def _slugify_workspace_name(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return base or "workspace"


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.workspace_repository = WorkspaceRepository(session)
        self.brand_profile_repository = BrandProfileRepository(session)
        self.activity_service = WorkspaceActivityEventService(session)

    async def create_workspace(self, payload: WorkspaceCreate) -> Workspace:
        slug = _slugify_workspace_name(payload.name)
        existing = await self.workspace_repository.get_by_slug(slug)
        if existing is not None:
            raise ConflictError("A workspace with this name already exists", code="workspace_slug_taken")

        workspace = Workspace(name=payload.name, slug=slug)
        owner = Member(
            workspace=workspace,
            full_name=payload.owner.full_name,
            email=payload.owner.email,
            role=MemberRole.OWNER,
        )
        self.session.add(owner)
        await self.workspace_repository.add(workspace)
        await self.session.flush()
        await self.activity_service.record_event(
            workspace_id=workspace.id,
            entity_type=ActivityEntityType.WORKSPACE,
            entity_id=workspace.id,
            event_type=ActivityEventType.WORKSPACE_CREATED,
            summary=f"Created workspace '{workspace.name}'.",
            actor_label=payload.owner.full_name,
            metadata_payload={"owner_email": payload.owner.email},
        )
        await self.session.commit()
        return workspace

    async def get_workspace(self, workspace_id: str) -> Workspace:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
        return workspace
