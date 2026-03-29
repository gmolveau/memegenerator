"""add_template_creator_id

Revision ID: a9f1e3b7c2d5
Revises: 6e886ea6bb5e
Create Date: 2026-03-28 00:00:00.000000
"""  # noqa: INP001

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision = "a9f1e3b7c2d5"
down_revision = "6e886ea6bb5e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    with op.batch_alter_table("templates") as batch_op:
        batch_op.add_column(sa.Column("creator_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_templates_creator_id_users",
            "users",
            ["creator_id"],
            ["id"],
        )


def downgrade() -> None:
    """Reverse the migration."""
    with op.batch_alter_table("templates") as batch_op:
        batch_op.drop_constraint("fk_templates_creator_id_users", type_="foreignkey")
        batch_op.drop_column("creator_id")
