from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking, BookingStatus
from app.hotels.rooms.rooms_model import Room
from app.shared.repository import BaseRepository


class BookingRepository(BaseRepository[
    Booking,
]):
    def __init__(self) -> None:
        super().__init__(Booking)

    async def get_by_id_and_user(
            self,
            session: AsyncSession,
            booking_id: int,
            user_id: int,
    ) -> Booking | None:
        result = await session.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
            self,
            session: AsyncSession,
            user_id: int,
    ) -> list[Booking]:
        result = await session.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def cancel_booking(
            self,
            booking: Booking,
            session: AsyncSession,
    ) -> Booking | None:
        booking.status = BookingStatus.CANCELLED

        await session.flush()

        return booking


    async def calculate_total_price(
            self,
            session: AsyncSession,
            room_id: int,
            check_in: date,
            check_out: date,
    ) -> int:
        stmt = (
        select(Room.price_per_night)
        .where(Room.id == room_id)
        )

        result = await session.execute(stmt)

        price_per_night = result.scalar_one_or_none()

        if price_per_night is None:
            raise ValueError(f"Room with id={room_id} not found")

        nights = (check_out - check_in).days

        if nights <= 0:
            raise ValueError("check_out must be after check_in")

        total_price = price_per_night * nights

        return total_price

    

    async def validate_booking(
            self,
            session: AsyncSession,
            room_id: int,
            check_in: date,
            check_out: date,
            guests: int,
        ) -> bool:

        if check_in >= check_out:
            raise ValueError("pass")

        conflict_booking_exists = (
            select(Booking.id)
            .where(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.CONFIRMED,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            ).exists()
        )
        room_capacity_exists = (
            select(Room.id)
            .where(
                Room.id == room_id,
                Room.capacity >= guests,
            )
            .exists()
        )

        stmt = select(conflict_booking_exists, room_capacity_exists)

        result = await session.execute(stmt)

        conflict_exists, capacity_is_enough = result.one()

        if conflict_exists:
            raise ValueError("Room is already booked for these dates")

        if not capacity_is_enough:
            raise ValueError("Room capacity is not enough for this number of guests")
        
        return True
