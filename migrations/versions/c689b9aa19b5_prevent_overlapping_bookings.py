"""prevent overlapping bookings

Revision ID: c689b9aa19b5
Revises: bb4ed3a75e77
Create Date: 2026-09-30 13:04:15.327980

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c689b9aa19b5"
down_revision: str | Sequence[str] | None = "bb4ed3a75e77"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_check_constraint(
        "ck_bookings_dates",
        "bookings",
        "check_out > check_in",
    )
    op.create_check_constraint(
        "ck_bookings_guests",
        "bookings",
        "guests > 0",
    )

    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT bookings_no_overlap
        EXCLUDE USING gist (
            room_id WITH =,
            daterange(check_in, check_out, '[)') WITH &&
        )
        WHERE (status = 'CONFIRMED')
    """)


def downgrade() -> None:
    op.drop_constraint(
        "bookings_no_overlap",
        "bookings",
    )
    op.drop_constraint(
        "ck_bookings_guests",
        "bookings",
        type_="check",
    )
    op.drop_constraint(
        "ck_bookings_dates",
        "bookings",
        type_="check",
    )
