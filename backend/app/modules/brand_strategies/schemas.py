from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.brand_strategies.models import StrategyStatus


class PlatformPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    brand_strategy_id: str
    platform_name: str
    objective: str
    cadence_summary: str
    content_mix: str
    success_signal: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class ContentPillarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    brand_strategy_id: str
    name: str
    description: str
    channel_angle: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class BrandStrategyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    source_workflow_run_id: str | None
    parent_strategy_id: str | None
    version_number: int
    is_active: bool
    status: StrategyStatus
    title: str
    summary: str
    positioning_statement: str
    audience_focus: str
    channel_focus: str
    campaign_note: str | None
    review_notes: str | None
    reviewed_by_member_id: str | None
    reviewed_at: datetime | None
    approved_at: datetime | None
    superseded_at: datetime | None
    platform_plans: list[PlatformPlanResponse]
    content_pillars: list[ContentPillarResponse]
    created_at: datetime
    updated_at: datetime


class BrandStrategyReviewUpdate(BaseModel):
    status: StrategyStatus = Field(default=StrategyStatus.IN_REVIEW)
    review_notes: str | None = Field(default=None, max_length=2000)
    reviewer_member_id: str | None = Field(default=None, max_length=36)
