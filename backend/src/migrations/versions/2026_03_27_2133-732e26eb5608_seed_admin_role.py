"""seed_admin_role

Revision ID: 732e26eb5608
Revises: 18eb37ad9bb7
Create Date: 2026-03-27 21:33:02.144888
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "732e26eb5608"
down_revision = "18eb37ad9bb7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    op.execute(sa.text("INSERT INTO roles (name) VALUES ('superadmin')"))


def downgrade() -> None:
    """Reverse the migration."""
    op.execute(sa.text("DELETE FROM roles WHERE name = 'superadmin'"))
