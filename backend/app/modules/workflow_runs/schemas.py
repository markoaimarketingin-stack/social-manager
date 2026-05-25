from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.brand_strategies.models import StrategyStatus
from app.modules.content_plans.models import ContentPlanStatus, PlannedPostStatus
from app.modules.post_drafts.models import DraftReviewStatus
from app.modules.workflow_runs.models import WorkflowStatus, WorkflowType


class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    input_payload: dict[str, Any]
    output_payload: dict[str, Any] | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
    initiated_by_member_id: str | None
    created_at: datetime
    updated_at: datetime


class StrategyWorkflowRequest(BaseModel):
    initiated_by_member_id: str | None = None
    goal: str = Field(default="Create an initial strategy foundation", max_length=500)


class StrategyWorkflowInput(BaseModel):
    workspace_id: str
    brand_profile_name: str
    industry: str
    voice_summary: str | None
    mission: str | None
    audience_segments: list[str]
    goal: str


class StrategyPlatformPlanArtifact(BaseModel):
    platform_name: str
    objective: str
    cadence_summary: str
    content_mix: str
    success_signal: str
    sort_order: int


class StrategyContentPillarArtifact(BaseModel):
    name: str
    description: str
    channel_angle: str
    sort_order: int


class StrategyWorkflowOutput(BaseModel):
    title: str
    summary: str
    positioning_statement: str
    audience_focus: str
    channel_focus: str
    campaign_note: str
    status: StrategyStatus = StrategyStatus.IN_REVIEW
    recommended_next_steps: list[str]
    platform_plans: list[StrategyPlatformPlanArtifact]
    content_pillars: list[StrategyContentPillarArtifact]


class ContentPlanWorkflowRequest(BaseModel):
    brand_strategy_id: str | None = None
    planning_horizon_label: str = Field(default="Next 2 weeks", max_length=80)
    initiated_by_member_id: str | None = None


class ContentPlanWorkflowInput(BaseModel):
    workspace_id: str
    brand_strategy_id: str
    strategy_title: str
    planning_horizon_label: str
    platform_names: list[str]
    content_pillars: list[str]


class PlannedPostArtifact(BaseModel):
    sequence_number: int
    scheduled_for: date
    platform: str
    format: str
    title: str
    hook: str
    angle: str
    call_to_action: str
    status: PlannedPostStatus = PlannedPostStatus.PLANNED
    notes: str | None = None
    content_pillar_name: str | None = None


class ContentPlanWorkflowOutput(BaseModel):
    title: str
    planning_horizon_label: str
    summary: str
    status: ContentPlanStatus = ContentPlanStatus.IN_REVIEW
    planned_posts: list[PlannedPostArtifact]


class DraftWorkflowRequest(BaseModel):
    content_plan_id: str | None = None
    initiated_by_member_id: str | None = None


class DraftWorkflowInput(BaseModel):
    workspace_id: str
    content_plan_id: str
    plan_title: str
    planned_posts: list[PlannedPostArtifact]


class DraftArtifact(BaseModel):
    planned_post_sequence_number: int
    title: str
    caption: str
    creative_brief: str
    call_to_action: str
    hashtags: list[str]
    review_status: DraftReviewStatus = DraftReviewStatus.IN_REVIEW


class DraftWorkflowOutput(BaseModel):
    summary: str
    generated_count: int
    drafts: list[DraftArtifact]
