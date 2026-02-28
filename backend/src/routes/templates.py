"""Meme templates endpoints."""

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.template import Template
from src.schemas.template import (
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdateRequest,
)
from src.services import templates as template_service
from src.storage import get_disk
from src.storage.disk import StorageDisk

router = APIRouter(prefix="/templates", tags=["templates"])


def _to_response(t: Template, disk: StorageDisk) -> TemplateResponse:
    return TemplateResponse(
        id=t.id,
        name=t.name,
        keywords=[k for k in t.keywords.split(",") if k],
        image_url=disk.url(t.filename),
        popularity=t.popularity,
        created_at=t.created_at,
    )


@router.get(path="", response_model=TemplateListResponse)
def list_templates(
    search: str | None = None,
    limit: int = Query(default=40, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(dependency=get_db),
    disk: StorageDisk = Depends(get_disk),
):
    templates, total = template_service.list_templates(
        db, search=search, limit=limit, offset=offset
    )
    return TemplateListResponse(
        templates=[_to_response(t, disk) for t in templates],
        total=total,
    )


@router.get(path="/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(dependency=get_db),
    disk: StorageDisk = Depends(get_disk),
):
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _to_response(template, disk)


@router.post(path="", response_model=TemplateResponse, status_code=201)
def upload_template(
    name: str = Form(...),
    keywords: str = Form(""),
    file: UploadFile = ...,
    db: Session = Depends(get_db),
    disk: StorageDisk = Depends(get_disk),
):
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    try:
        template: Template = template_service.create_template(
            db, disk, name, keyword_list, file
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(template, disk)


@router.patch(path="/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    body: TemplateUpdateRequest,
    db: Session = Depends(dependency=get_db),
    disk: StorageDisk = Depends(get_disk),
):
    template = template_service.update_template(
        db, template_id, name=body.name, keywords=body.keywords
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return _to_response(template, disk)


@router.post(path="/{template_id}/popularity", status_code=204)
def increment_popularity(
    template_id: int,
    db: Session = Depends(dependency=get_db),
):
    if not template_service.increment_popularity(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")


@router.delete(path="/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(dependency=get_db),
    disk: StorageDisk = Depends(get_disk),
):
    if not template_service.delete_template(db, disk, template_id):
        raise HTTPException(status_code=404, detail="Template not found")
