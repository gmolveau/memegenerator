import click

from src.cli.templates import templates_group
from src.cli.users import users_group


@click.group()
def cli():
    pass


cli.add_command(templates_group)
cli.add_command(users_group)
