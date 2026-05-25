from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.brand_strategies.schemas import BrandStrategyResponse, BrandStrategyReviewUpdate
from app.modules.brand_strategies.service import BrandStrategyService

router = APIRouter(tags=["brand_strategies"])


@router.get("/workspaces/{workspace_id}/strategies", response_model=list[BrandStrategyResponse])
async def list_brand_strategies(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[BrandStrategyResponse]:
    service = BrandStrategyService(session)
    strategies = await service.list_strategies(workspace_id)
    return [BrandStrategyResponse.model_validate(strategy) for strategy in strategies]


@router.get("/workspaces/{workspace_id}/strategies/latest", response_model=BrandStrategyResponse)
async def get_latest_brand_strategy(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> BrandStrategyResponse:
    service = BrandStrategyService(session)
    strategy = await service.get_latest_strategy(workspace_id)
    return BrandStrategyResponse.model_validate(strategy)


@router.get("/strategies/{strategy_id}", response_model=BrandStrategyResponse)
async def get_brand_strategy(
    strategy_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> BrandStrategyResponse:
    service = BrandStrategyService(session)
    strategy = await service.get_strategy(strategy_id)
    return BrandStrategyResponse.model_validate(strategy)


@router.patch("/strategies/{strategy_id}/review", response_model=BrandStrategyResponse)
async def review_brand_strategy(
    strategy_id: str,
    payload: BrandStrategyReviewUpdate,
    session: AsyncSession = Depends(db_session_dependency),
) -> BrandStrategyResponse:
    service = BrandStrategyService(session)
    strategy = await service.review_strategy(strategy_id, payload)
    return BrandStrategyResponse.model_validate(strategy)
