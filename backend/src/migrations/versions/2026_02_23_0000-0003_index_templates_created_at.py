"""index templates.created_at

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-23 00:00:00
"""  # noqa: INP001

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    op.create_index("ix_templates_created_at", "templates", ["created_at"])


def downgrade() -> None:
    """Reverse the migration."""
    op.drop_index("ix_templates_created_at", table_name="templates")
