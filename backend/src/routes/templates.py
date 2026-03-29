"""Meme templates endpoints."""

import json
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile
from starlette.requests import Request

from src.dependencies import ADMIN_ROLES, AdminDep, CurrentUserDep, DiskDep, SessionDep
from src.models import Template
from src.schemas.template import (
    TemplateListResponse,
    TemplateResponse,
    TemplateTextLayerSchema,
    TemplateUpdateRequest,
)
from src.services import templates as template_service
from src.storage.disk import StorageDisk

router = APIRouter(prefix="/templates", tags=["templates"])


def _to_response(t: Template, disk: StorageDisk) -> TemplateResponse:
    try:
        raw_layers = json.loads(t.text_layers or "[]")
        text_layers = [TemplateTextLayerSchema(**layer) for layer in raw_layers]
    except Exception:
        text_layers = []
    return TemplateResponse(
        id=t.id,
        name=t.name,
        keywords=[k for k in t.keywords.split(",") if k],
        image_url=disk.url(t.filename),
        popularity=t.popularity,
        created_at=t.created_at,
        text_layers=text_layers,
    )


@router.get(path="", response_model=TemplateListResponse)
def list_templates(
    db: SessionDep,
    disk: DiskDep,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 40,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    templates, total = template_service.list_templates(
        db, search=search, limit=limit, offset=offset
    )
    return TemplateListResponse(
        templates=[_to_response(t, disk) for t in templates],
        total=total,
    )


@router.get(path="/mine", response_model=TemplateListResponse)
def list_my_templates(
    db: SessionDep,
    disk: DiskDep,
    current_user: CurrentUserDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 40,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    templates, total = template_service.list_templates_by_creator(
        db, current_user.id, limit=limit, offset=offset
    )
    return TemplateListResponse(
        templates=[_to_response(t, disk) for t in templates],
        total=total,
    )


@router.get(path="/{template_id}", response_model=TemplateResponse)
def get_template(
    db: SessionDep,
    disk: DiskDep,
    template_id: int,
):
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _to_response(template, disk)


@router.post(path="", response_model=TemplateResponse, status_code=201)
def upload_template(
    db: SessionDep,
    disk: DiskDep,
    current_user: CurrentUserDep,
    name: Annotated[str, Form()],
    file: Annotated[UploadFile, Form()],
    keywords: Annotated[str, Form()] = "",
):
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    try:
        template: Template = template_service.create_template(
            db,
            disk,
            name,
            keyword_list,
            file,
            creator_id=current_user.id if current_user else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(template, disk)


@router.patch(path="/{template_id}", response_model=TemplateResponse)
def update_template(
    request: Request,
    db: SessionDep,
    disk: DiskDep,
    current_user: CurrentUserDep,
    template_id: int,
    body: TemplateUpdateRequest,
):
    session_user = request.session.get("user")
    if not session_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    is_admin = session_user.get("role") in ADMIN_ROLES
    is_creator = current_user is not None and template.creator_id == current_user.id
    if not is_admin and not is_creator:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = template_service.update_template(
        db,
        template_id,
        name=body.name,
        keywords=body.keywords,
        text_layers=[layer.model_dump() for layer in body.text_layers]
        if body.text_layers is not None
        else None,
    )
    assert updated is not None
    return _to_response(updated, disk)


@router.post(path="/{template_id}/popularity", status_code=204)
def increment_popularity(
    db: SessionDep,
    template_id: int,
):
    if not template_service.increment_popularity(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")


@router.delete(path="/{template_id}", status_code=204, dependencies=[AdminDep])
def delete_template(
    db: SessionDep,
    disk: DiskDep,
    template_id: int,
):
    if not template_service.delete_template(db, disk, template_id):
        raise HTTPException(status_code=404, detail="Template not found")
