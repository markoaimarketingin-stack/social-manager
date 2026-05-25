from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.workspaces.models import Workspace


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, workspace: Workspace) -> Workspace:
        self.session.add(workspace)
        await self.session.flush()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: str) -> Workspace | None:
        result = await self.session.execute(
            select(Workspace)
            .options(
                selectinload(Workspace.members),
                selectinload(Workspace.brand_profile),
                selectinload(Workspace.audience_segments),
            )
            .where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Workspace | None:
        result = await self.session.execute(select(Workspace).where(Workspace.slug == slug))
        return result.scalar_one_or_none()
