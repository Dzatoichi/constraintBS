from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking, BookingStatus
from app.hotels.rooms.rooms_model import Room
from app.shared.repository import BaseRepository


class BookingRepository(BaseRepository[Booking,]):
    def __init__(self) -> None:
        super().__init__(Booking)

    async def create(
        self,
        session: AsyncSession,
        payload: dict[str, Any],
    ) -> Booking:
        # Serialize inserts for one room before PostgreSQL checks exclusion.
        # The transaction owner (service) releases this lock on commit/rollback.
        await session.execute(
            select(Room.id).where(Room.id == payload["room_id"]).with_for_update()
        )
        booking = Booking(**payload)
        session.add(booking)
        await session.flush()
        return booking

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

    async def get_room(
        self,
        session: AsyncSession,
        room_id: int,
    ) -> Room | None:
        return await session.get(Room, room_id)

    async def has_conflict(
        self,
        session: AsyncSession,
        room_id: int,
        check_in: date,
        check_out: date,
    ) -> bool:
        statement = select(
            select(Booking.id)
            .where(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.CONFIRMED,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .exists()
        )
        return bool(await session.scalar(statement))
