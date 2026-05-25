from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class BrandProfileUpsert(BaseModel):
    brand_name: str = Field(min_length=2, max_length=120)
    industry: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    website_url: HttpUrl | None = None
    voice_summary: str | None = Field(default=None, max_length=1000)
    mission: str | None = Field(default=None, max_length=1000)


class BrandProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    brand_name: str
    industry: str
    description: str | None
    website_url: str | None
    voice_summary: str | None
    mission: str | None
    created_at: datetime
    updated_at: datetime
