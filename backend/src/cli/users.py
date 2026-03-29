import click

from src.database import SessionLocal
from src.services.users import assign_role


@click.group("users")
def users_group():
    pass


@users_group.command("give-admin")
@click.argument("identifier")
def cli_give_admin(identifier: str):
    """Give the admin role to a user by their username or sub."""
    with SessionLocal() as db:
        user = assign_role(db, identifier=identifier, role_name="admin")

    if user is None:
        click.echo(
            f"User or admin role not found for identifier: {identifier!r}", err=True
        )
        raise SystemExit(1)

    click.echo(f"Admin role assigned to {user.name} ({user.sub}).")
