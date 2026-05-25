from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkspaceOwnerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized_value = value.strip()
        if "@" not in normalized_value:
            raise ValueError("A valid email address is required")
        return normalized_value


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    owner: WorkspaceOwnerCreate


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class WorkspaceDetailResponse(WorkspaceResponse):
    brand_profile_id: str | None = None
    member_count: int
    audience_segment_count: int
