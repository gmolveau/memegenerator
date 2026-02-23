"""Template service — CRUD and file handling."""

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.models.template import Template

TEMPLATES_DIR = Path("data/templates")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def list_templates(db: Session, search: str | None = None) -> list[Template]:
    query = db.query(Template)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(Template.name.ilike(term) | Template.keywords.ilike(term))
    return query.order_by(Template.created_at.desc()).all()


def get_template(db: Session, template_id: int) -> Template | None:
    return db.query(Template).filter(Template.id == template_id).first()


def create_template(
    db: Session, name: str, keywords: list[str], file: UploadFile
) -> Template:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    ext = EXTENSION_MAP[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = TEMPLATES_DIR / filename
    with dest.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    template = Template(
        name=name,
        filename=filename,
        keywords=",".join(k.strip() for k in keywords if k.strip()),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template_id: int) -> bool:
    template = get_template(db, template_id)
    if not template:
        return False
    path = TEMPLATES_DIR / template.filename
    if path.exists():
        path.unlink()
    db.delete(template)
    db.commit()
    return True
