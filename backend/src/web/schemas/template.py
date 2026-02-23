"""Pydantic schemas for template endpoints."""

from datetime import datetime

from pydantic import BaseModel


class TemplateResponse(BaseModel):
    id: int
    name: str
    keywords: list[str]
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]
    total: int
