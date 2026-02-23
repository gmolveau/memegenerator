"""Meme templates endpoints."""

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.template import Template
from src.services import templates as template_service
from src.web.schemas.template import TemplateListResponse, TemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get(path="", response_model=TemplateListResponse)
def list_templates(
    search: str | None = None,
    db: Session = Depends(dependency=get_db),
):
    templates: list[Template] = template_service.list_templates(db, search=search)
    # We need the base URL; use a simple relative path the client will resolve
    items = [
        TemplateResponse(
            id=t.id,
            name=t.name,
            keywords=[k for k in t.keywords.split(",") if k],
            image_url=f"/static/templates/{t.filename}",
            created_at=t.created_at,
        )
        for t in templates
    ]
    return TemplateListResponse(templates=items, total=len(items))


@router.get(path="/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(dependency=get_db)):
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(
        id=template.id,
        name=template.name,
        keywords=[k for k in template.keywords.split(",") if k],
        image_url=f"/static/templates/{template.filename}",
        created_at=template.created_at,
    )


@router.post(path="", response_model=TemplateResponse, status_code=201)
def upload_template(
    name: str = Form(...),
    keywords: str = Form(""),
    file: UploadFile = ...,
    db: Session = Depends(get_db),
):
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    try:
        template: Template = template_service.create_template(
            db, name, keyword_list, file
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TemplateResponse(
        id=template.id,
        name=template.name,
        keywords=[k for k in template.keywords.split(sep=",") if k],
        image_url=f"/static/templates/{template.filename}",
        created_at=template.created_at,
    )


@router.delete(path="/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(dependency=get_db)):
    if not template_service.delete_template(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")
