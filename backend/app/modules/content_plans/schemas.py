from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.content_plans.models import ContentPlanStatus, PlannedPostStatus


class PlannedPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content_plan_id: str
    workspace_id: str
    brand_strategy_id: str
    content_pillar_id: str | None
    sequence_number: int
    scheduled_for: date
    platform: str
    format: str
    title: str
    hook: str
    angle: str
    call_to_action: str
    status: PlannedPostStatus
    notes: str | None
    approved_at: datetime | None
    publish_ready_at: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ContentPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    brand_strategy_id: str
    source_workflow_run_id: str | None
    parent_plan_id: str | None
    version_number: int
    is_active: bool
    title: str
    planning_horizon_label: str
    summary: str
    status: ContentPlanStatus
    review_notes: str | None
    reviewed_by_member_id: str | None
    reviewed_at: datetime | None
    approved_at: datetime | None
    superseded_at: datetime | None
    planned_posts: list[PlannedPostResponse]
    created_at: datetime
    updated_at: datetime


class ContentPlanGenerateRequest(BaseModel):
    brand_strategy_id: str | None = None
    planning_horizon_label: str = Field(default="Next 2 weeks", max_length=80)
    initiated_by_member_id: str | None = None


class PlannedPostUpdate(BaseModel):
    scheduled_for: date
    platform: str = Field(min_length=2, max_length=80)
    format: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=160)
    hook: str = Field(min_length=2, max_length=1000)
    angle: str = Field(min_length=2, max_length=1200)
    call_to_action: str = Field(min_length=2, max_length=600)
    status: PlannedPostStatus = PlannedPostStatus.PLANNED
    notes: str | None = Field(default=None, max_length=2000)
    reviewer_member_id: str | None = Field(default=None, max_length=36)
