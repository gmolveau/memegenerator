import click

from src.db.database import SessionLocal
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
