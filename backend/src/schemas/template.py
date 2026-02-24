"""Pydantic schemas for template endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class TemplateResponse(BaseModel):
    id: int
    name: str
    keywords: list[str]
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    keywords: list[str] = Field(..., min_length=1)


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]
    total: int
