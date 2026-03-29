"""add_session_token

Revision ID: c60fc7254dc9
Revises: 732e26eb5608
Create Date: 2026-03-27 21:37:20.770336
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "c60fc7254dc9"
down_revision = "732e26eb5608"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.add_column(
            sa.Column("token", sa.String(length=255), nullable=False, server_default="")
        )
        batch_op.create_unique_constraint("uq_sessions_token", ["token"])


def downgrade() -> None:
    """Reverse the migration."""
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.drop_constraint("uq_sessions_token", type_="unique")
        batch_op.drop_column("token")
