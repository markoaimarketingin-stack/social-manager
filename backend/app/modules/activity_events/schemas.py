from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.modules.activity_events.models import ActivityEntityType, ActivityEventType


class WorkspaceActivityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    actor_member_id: str | None
    actor_label: str | None
    entity_type: ActivityEntityType
    entity_id: str | None
    event_type: ActivityEventType
    summary: str
    metadata_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WorkspaceActivitySummaryResponse(BaseModel):
    total_events: int
    workflow_completions: int
    approvals: int
    publish_ready_items: int
    latest_event_at: datetime | None
    latest_summary: str | None
