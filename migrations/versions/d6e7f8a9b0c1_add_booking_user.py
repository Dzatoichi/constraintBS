"""add booking user

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-09-17 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6e7f8a9b0c1"
down_revision: str | Sequence[str] | None = "c5d6e7f8a9b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_user_id_users",
        "bookings",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_bookings_user_id"), "bookings", ["user_id"], unique=False)
    op.execute(
        "UPDATE bookings SET user_id = users.id "
        "FROM users WHERE bookings.guest_email = users.email"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_bookings_user_id"), table_name="bookings")
    op.drop_constraint("fk_bookings_user_id_users", "bookings", type_="foreignkey")
    op.drop_column("bookings", "user_id")
