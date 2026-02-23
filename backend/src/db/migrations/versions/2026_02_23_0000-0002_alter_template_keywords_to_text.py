"""alter template keywords to text

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-23 00:00:00
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    op.alter_column(
        "templates",
        "keywords",
        type_=sa.Text,
        existing_nullable=False,
        existing_server_default="",
    )


def downgrade() -> None:
    """Reverse the migration."""
    op.alter_column(
        "templates",
        "keywords",
        type_=sa.String(1000),
        existing_nullable=False,
        existing_server_default="",
    )
