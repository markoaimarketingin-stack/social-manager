from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.activity_events.models import ActivityEntityType, ActivityEventType
from app.modules.activity_events.service import WorkspaceActivityEventService
from app.modules.brand_strategies.models import BrandStrategy
from app.modules.brand_strategies.models import StrategyStatus
from app.modules.brand_strategies.repository import BrandStrategyRepository
from app.modules.brand_strategies.schemas import BrandStrategyReviewUpdate
from app.modules.workspaces.repository import WorkspaceRepository


class BrandStrategyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.brand_strategy_repository = BrandStrategyRepository(session)
        self.workspace_repository = WorkspaceRepository(session)
        self.activity_service = WorkspaceActivityEventService(session)

    async def list_strategies(self, workspace_id: str) -> list[BrandStrategy]:
        await self._ensure_workspace_exists(workspace_id)
        return await self.brand_strategy_repository.list_by_workspace_id(workspace_id)

    async def get_latest_strategy(self, workspace_id: str) -> BrandStrategy:
        await self._ensure_workspace_exists(workspace_id)
        strategy = await self.brand_strategy_repository.get_active_by_workspace_id(workspace_id)
        if strategy is None:
            strategy = await self.brand_strategy_repository.get_latest_by_workspace_id(workspace_id)
        if strategy is None:
            raise NotFoundError("Strategy not found", code="strategy_not_found")
        return strategy

    async def get_strategy(self, strategy_id: str) -> BrandStrategy:
        strategy = await self.brand_strategy_repository.get_by_id(strategy_id)
        if strategy is None:
            raise NotFoundError("Strategy not found", code="strategy_not_found")
        return strategy

    async def review_strategy(self, strategy_id: str, payload: BrandStrategyReviewUpdate) -> BrandStrategy:
        strategy = await self.get_strategy(strategy_id)
        strategy.status = payload.status
        strategy.review_notes = payload.review_notes
        strategy.reviewed_by_member_id = payload.reviewer_member_id
        strategy.reviewed_at = datetime.now(timezone.utc)
        if payload.status == StrategyStatus.APPROVED:
            strategy.approved_at = datetime.now(timezone.utc)
        if payload.status == StrategyStatus.REJECTED:
            strategy.is_active = True

        await self.brand_strategy_repository.save(strategy)
        await self.activity_service.record_event(
            workspace_id=strategy.workspace_id,
            entity_type=ActivityEntityType.STRATEGY,
            entity_id=strategy.id,
            event_type=ActivityEventType.STRATEGY_REVIEWED,
            summary=f"Reviewed strategy v{strategy.version_number} as {payload.status.value}.",
            actor_member_id=payload.reviewer_member_id,
            actor_label="Reviewer",
            metadata_payload={
                "status": payload.status.value,
                "version_number": strategy.version_number,
            },
        )
        if payload.status == StrategyStatus.APPROVED:
            await self.activity_service.record_event(
                workspace_id=strategy.workspace_id,
                entity_type=ActivityEntityType.STRATEGY,
                entity_id=strategy.id,
                event_type=ActivityEventType.APPROVAL_GRANTED,
                summary=f"Approved strategy v{strategy.version_number} for planning.",
                actor_member_id=payload.reviewer_member_id,
                actor_label="Reviewer",
                metadata_payload={"version_number": strategy.version_number},
            )
        await self.session.commit()
        return strategy

    async def _ensure_workspace_exists(self, workspace_id: str) -> None:
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise NotFoundError("Workspace not found", code="workspace_not_found")
