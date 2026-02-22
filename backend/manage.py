import click
from src.cli.example import example_group


@click.group()
def all_commands():
    pass


# Add script handlers here
all_commands.add_command(example_group)


if __name__ == "__main__":
    all_commands()
