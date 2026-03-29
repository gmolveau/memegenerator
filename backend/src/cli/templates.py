import json
import uuid
from pathlib import Path

import click

from src.database import SessionLocal
from src.models import Template
from src.services import templates as template_service
from src.storage import active_disk


@click.group("templates")
def templates_group():
    pass


@templates_group.command("delete")
@click.argument("template_id", type=int)
def cli_delete_template(template_id: int):
    """Delete a template and its associated image by ID."""
    with SessionLocal() as db:
        deleted = template_service.delete_template(db, active_disk, template_id)

    if not deleted:
        click.echo(f"Template {template_id} not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Template {template_id} deleted.")


@templates_group.command("load-samples")
@click.argument(
    "data_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument(
    "images_dir", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def cli_load_samples(data_file: Path, images_dir: Path):
    """Load sample templates from DATA_FILE (JSON) and IMAGES_DIR."""
    entries = json.loads(data_file.read_text())

    loaded = 0
    skipped = 0
    with SessionLocal() as db:
        for entry in entries:
            title: str = entry["title"]
            filename: str = entry["filename"]
            keywords: str = entry.get("keywords", "")

            image_path = images_dir / filename
            if not image_path.exists():
                click.echo(f"  skip  {filename} (file not found)", err=True)
                skipped += 1
                continue

            ext = image_path.suffix
            stored_name = f"{uuid.uuid4().hex}{ext}"
            with image_path.open("rb") as f:
                active_disk.save(stored_name, f)

            template = Template(name=title, filename=stored_name, keywords=keywords)
            db.add(template)
            db.commit()
            click.echo(f"  ok    {title}")
            loaded += 1

    click.echo(f"\nDone: {loaded} loaded, {skipped} skipped.")
