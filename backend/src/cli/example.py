import click


@click.group()
def example_group():
    pass


@example_group.command("test")
def cli_create_dev_roles():
    print("OK")
