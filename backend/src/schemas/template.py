"""Pydantic schemas for template endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TemplateTextLayerSchema(BaseModel):
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0
    fontSize: int = 36
    fontFamily: str = "Impact"
    color: str = "#ffffff"
    outlineColor: str = "#000000"
    outlineWidth: int = 2
    align: Literal["left", "center", "right"] = "center"
    verticalAlign: Literal["top", "middle", "bottom"] = "middle"
    bold: bool = False
    italic: bool = False
    allCaps: bool = False


class TemplateResponse(BaseModel):
    id: int
    name: str
    keywords: list[str]
    image_url: str
    popularity: int
    created_at: datetime
    text_layers: list[TemplateTextLayerSchema]

    model_config = {"from_attributes": True}


class TemplateUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    keywords: list[str] = Field(..., min_length=1)
    text_layers: list[TemplateTextLayerSchema] | None = None


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]
    total: int
