from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AudienceSegmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1500)
    age_range: str | None = Field(default=None, max_length=80)
    interests: list[str] = Field(default_factory=list, max_length=10)
    primary_platform: str | None = Field(default=None, max_length=80)
    messaging_angle: str | None = Field(default=None, max_length=1000)


class AudienceSegmentUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1500)
    age_range: str | None = Field(default=None, max_length=80)
    interests: list[str] = Field(default_factory=list, max_length=10)
    primary_platform: str | None = Field(default=None, max_length=80)
    messaging_angle: str | None = Field(default=None, max_length=1000)


class AudienceSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    description: str | None
    age_range: str | None
    interests: list[str]
    primary_platform: str | None
    messaging_angle: str | None
    created_at: datetime
    updated_at: datetime
