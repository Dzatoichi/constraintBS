from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking, BookingStatus
from app.bookings.booking_schemas import BookingCreate, BookingUpdate
from app.shared.repository import BaseRepository


class BookingRepository(BaseRepository[
    Booking,
    BookingCreate,
    BookingUpdate,
]):
    def __init__(self) -> None:
        super().__init__(Booking)

    async def cancel_booking(
            self,
            booking: Booking,
            session: AsyncSession,
    ) -> Booking | None:
        booking.status = BookingStatus.CANCELLED

        await session.flush()

        return booking

