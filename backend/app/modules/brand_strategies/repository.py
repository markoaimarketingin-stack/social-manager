from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.brand_strategies.models import BrandStrategy


class BrandStrategyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_workspace_id(self, workspace_id: str) -> list[BrandStrategy]:
        result = await self.session.execute(
            select(BrandStrategy)
            .options(
                selectinload(BrandStrategy.platform_plans),
                selectinload(BrandStrategy.content_pillars),
            )
            .where(BrandStrategy.workspace_id == workspace_id)
            .order_by(BrandStrategy.version_number.desc(), BrandStrategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_workspace_id(self, workspace_id: str) -> BrandStrategy | None:
        result = await self.session.execute(
            select(BrandStrategy)
            .options(
                selectinload(BrandStrategy.platform_plans),
                selectinload(BrandStrategy.content_pillars),
            )
            .where(BrandStrategy.workspace_id == workspace_id)
            .order_by(BrandStrategy.version_number.desc(), BrandStrategy.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active_by_workspace_id(self, workspace_id: str) -> BrandStrategy | None:
        result = await self.session.execute(
            select(BrandStrategy)
            .options(
                selectinload(BrandStrategy.platform_plans),
                selectinload(BrandStrategy.content_pillars),
            )
            .where(BrandStrategy.workspace_id == workspace_id, BrandStrategy.is_active.is_(True))
            .order_by(BrandStrategy.version_number.desc(), BrandStrategy.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, strategy_id: str) -> BrandStrategy | None:
        result = await self.session.execute(
            select(BrandStrategy)
            .options(
                selectinload(BrandStrategy.platform_plans),
                selectinload(BrandStrategy.content_pillars),
            )
            .where(BrandStrategy.id == strategy_id)
        )
        return result.scalar_one_or_none()

    async def get_next_version_number(self, workspace_id: str) -> int:
        result = await self.session.execute(
            select(func.max(BrandStrategy.version_number)).where(BrandStrategy.workspace_id == workspace_id)
        )
        current_max = result.scalar_one()
        return (current_max or 0) + 1

    async def save(self, brand_strategy: BrandStrategy) -> BrandStrategy:
        self.session.add(brand_strategy)
        await self.session.flush()
        await self.session.refresh(brand_strategy)
        return brand_strategy
