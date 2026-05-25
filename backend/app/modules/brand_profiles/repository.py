from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brand_profiles.models import BrandProfile


class BrandProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_workspace_id(self, workspace_id: str) -> BrandProfile | None:
        result = await self.session.execute(
            select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def save(self, brand_profile: BrandProfile) -> BrandProfile:
        self.session.add(brand_profile)
        await self.session.flush()
        await self.session.refresh(brand_profile)
        return brand_profile
