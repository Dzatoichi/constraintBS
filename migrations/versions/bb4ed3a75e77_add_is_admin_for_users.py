"""add is_admin for users

Revision ID: bb4ed3a75e77
Revises: e7f8a9b0c1d2
Create Date: 2026-09-27 18:36:44.178176
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "bb4ed3a75e77"
down_revision: str | Sequence[str] | None = "e7f8a9b0c1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
