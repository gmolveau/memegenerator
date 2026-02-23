"""create templates table

Revision ID: 0001
Revises:
Create Date: 2026-02-23 00:00:00
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False, unique=True),
        sa.Column("keywords", sa.String(1000), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Reverse the migration."""
    op.drop_table("templates")
