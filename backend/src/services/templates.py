"""Template service — CRUD and file handling."""

import uuid

from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.template import Template
from src.storage.disk import StorageDisk

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def list_templates(
    db: Session,
    search: str | None = None,
    limit: int = 40,
    offset: int = 0,
) -> tuple[list[Template], int]:
    filters = []
    if search:
        term = f"%{search.lower()}%"
        filters.append(Template.name.ilike(term) | Template.keywords.ilike(term))

    # Single query: fetch rows + total via window function (one DB round-trip)
    total_col = func.count().over().label("total")
    rows = (
        db.query(Template, total_col)
        .filter(*filters)
        .order_by(Template.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    if not rows:
        return [], 0
    return [r for r, _ in rows], rows[0].total


def get_template(db: Session, template_id: int) -> Template | None:
    return db.query(Template).filter(Template.id == template_id).first()


def create_template(
    db: Session, disk: StorageDisk, name: str, keywords: list[str], file: UploadFile
) -> Template:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    ext = EXTENSION_MAP[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    disk.save(filename, file.file)

    template = Template(
        name=name,
        filename=filename,
        keywords=",".join(k.strip() for k in keywords if k.strip()),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(
    db: Session,
    template_id: int,
    name: str,
    keywords: list[str],
) -> Template | None:
    template = get_template(db, template_id)
    if not template:
        return None
    template.name = name
    template.keywords = ",".join(k.strip() for k in keywords if k.strip())
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, disk: StorageDisk, template_id: int) -> bool:
    template = get_template(db, template_id)
    if not template:
        return False
    disk.delete(template.filename)
    db.delete(template)
    db.commit()
    return True
