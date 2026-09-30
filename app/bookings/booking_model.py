import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

if TYPE_CHECKING:
    from app.users.users_model import User


class BookingStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cacnelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    guest_name: Mapped[str] = mapped_column(String(100), nullable=False)
    guest_email: Mapped[str] = mapped_column(String(255), nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"))
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user: Mapped["User | None"] = relationship("User", back_populates="bookings")

    __table_args__ = (
        CheckConstraint(
            "check_out > check_in",
            name="ck_bookings_dates",
        ),
        CheckConstraint(
            "guests > 0",
            name="ck_bookings_guests",
        ),
        ExcludeConstraint(
            ("room_id", "="),
            (func.daterange(check_in, check_out, "[)"), "&&"),
            where=text("status = 'CONFIRMED'"),
            using="gist",
            name="bookings_no_overlap",
        ),
    )
