from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.brand_profiles.models import BrandProfile
from app.modules.brand_profiles.repository import BrandProfileRepository
from app.modules.brand_profiles.schemas import BrandProfileUpsert
from app.modules.workspaces.repository import WorkspaceRepository


class BrandProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.brand_profile_repository = BrandProfileRepository(session)
        self.workspace_repository = WorkspaceRepository(session)

    async def get_brand_profile(self, workspace_id: str) -> BrandProfile:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")

        brand_profile = await self.brand_profile_repository.get_by_workspace_id(workspace_id)
        if brand_profile is None:
            raise NotFoundError("Brand profile not found", code="brand_profile_not_found")
        return brand_profile

    async def upsert_brand_profile(self, workspace_id: str, payload: BrandProfileUpsert) -> BrandProfile:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")

        brand_profile = await self.brand_profile_repository.get_by_workspace_id(workspace_id)
        if brand_profile is None:
            brand_profile = BrandProfile(
                workspace_id=workspace_id,
                brand_name=payload.brand_name,
                industry=payload.industry,
                description=payload.description,
                website_url=str(payload.website_url) if payload.website_url else None,
                voice_summary=payload.voice_summary,
                mission=payload.mission,
            )
        else:
            brand_profile.brand_name = payload.brand_name
            brand_profile.industry = payload.industry
            brand_profile.description = payload.description
            brand_profile.website_url = str(payload.website_url) if payload.website_url else None
            brand_profile.voice_summary = payload.voice_summary
            brand_profile.mission = payload.mission

        await self.brand_profile_repository.save(brand_profile)
        await self.session.commit()
        return brand_profile
