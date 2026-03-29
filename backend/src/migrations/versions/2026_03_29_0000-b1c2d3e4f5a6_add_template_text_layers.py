"""add_template_text_layers

Revision ID: b1c2d3e4f5a6
Revises: a9f1e3b7c2d5
Create Date: 2026-03-29 00:00:00.000000
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "b1c2d3e4f5a6"
down_revision = "a9f1e3b7c2d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    with op.batch_alter_table("templates") as batch_op:
        batch_op.add_column(
            sa.Column("text_layers", sa.Text(), nullable=False, server_default="[]")
        )


def downgrade() -> None:
    """Reverse the migration."""
    with op.batch_alter_table("templates") as batch_op:
        batch_op.drop_column("text_layers")
