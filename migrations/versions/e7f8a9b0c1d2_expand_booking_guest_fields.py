"""expand booking guest fields

Revision ID: e7f8a9b0c1d2
Revises: d6e7f8a9b0c1
Create Date: 2026-09-17 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: str | Sequence[str] | None = "d6e7f8a9b0c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "bookings",
        "guest_name",
        existing_type=sa.String(length=20),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    op.alter_column(
        "bookings",
        "guest_email",
        existing_type=sa.String(length=20),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "bookings",
        "guest_email",
        existing_type=sa.String(length=255),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
    op.alter_column(
        "bookings",
        "guest_name",
        existing_type=sa.String(length=100),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
