"""add template popularity

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-24 00:00:00
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    op.add_column(
        "templates",
        sa.Column("popularity", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Reverse the migration."""
    op.drop_column("templates", "popularity")
