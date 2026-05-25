from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.modules.brand_profiles.schemas import BrandProfileResponse, BrandProfileUpsert
from app.modules.brand_profiles.service import BrandProfileService

router = APIRouter(prefix="/workspaces/{workspace_id}/brand-profile", tags=["brand_profiles"])


@router.get("", response_model=BrandProfileResponse)
async def get_brand_profile(
    workspace_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> BrandProfileResponse:
    service = BrandProfileService(session)
    brand_profile = await service.get_brand_profile(workspace_id)
    return BrandProfileResponse.model_validate(brand_profile)


@router.put("", response_model=BrandProfileResponse)
async def upsert_brand_profile(
    workspace_id: str,
    payload: BrandProfileUpsert,
    session: AsyncSession = Depends(db_session_dependency),
) -> BrandProfileResponse:
    service = BrandProfileService(session)
    brand_profile = await service.upsert_brand_profile(workspace_id, payload)
    return BrandProfileResponse.model_validate(brand_profile)
