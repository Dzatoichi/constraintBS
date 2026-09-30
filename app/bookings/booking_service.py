from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking
from app.bookings.booking_repository import BookingRepository
from app.bookings.booking_schemas import BookingCreate
from app.bookings.errors import BookingConflict, BookingNotFound, InvalidBookingDates
from app.hotels.rooms.errors import RoomCapacityExceeded, RoomNotFound
from app.users.users_model import User


class BookingService:
    def __init__(
        self,
        booking_repository: BookingRepository,
    ) -> None:
        self.booking_repository = booking_repository

    async def create_booking(
        self,
        session: AsyncSession,
        data: BookingCreate,
        user: User,
    ) -> Booking | None:
        """
        Создание бронирования
        """
        if data.check_out <= data.check_in:
            raise InvalidBookingDates()

        room = await self.booking_repository.get_room(session, data.room_id)
        if room is None:
            raise RoomNotFound()
        if data.guests > room.capacity:
            raise RoomCapacityExceeded()
        if await self.booking_repository.has_conflict(
            session,
            data.room_id,
            data.check_in,
            data.check_out,
        ):
            raise BookingConflict()

        total_price = room.price_per_night * (data.check_out - data.check_in).days

        payload = data.model_dump()

        payload["total_price"] = total_price
        payload["user_id"] = user.id
        payload["guest_name"] = user.full_name or user.username
        payload["guest_email"] = user.email

        try:
            booking = await self.booking_repository.create(
                payload=payload,
                session=session,
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            original_error = exc.orig
            if original_error is None:
                raise
            driver_error = original_error.__cause__
            if (
                getattr(original_error, "sqlstate", None) == "23P01"
                and getattr(driver_error, "constraint_name", None)
                == "bookings_no_overlap"
            ):
                raise BookingConflict() from exc
            raise
        await session.refresh(booking)

        return booking

    async def get_booking(
        self,
        booking_id: int,
        session: AsyncSession,
    ) -> Booking:
        """
        Получение бронирования ID
        """
        booking = await self.booking_repository.get_by_id(
            obj_id=booking_id,
            session=session,
        )

        if booking is None:
            raise BookingNotFound()

        return booking

    async def get_bookings(
        self,
        session: AsyncSession,
    ) -> list[Booking]:
        """
        Получение бронирований
        """
        return (
            await self.booking_repository.get_all(
                session=session,
            )
            or []
        )

    async def cancel_booking(
        self,
        booking_id: int,
        session: AsyncSession,
        user_id: int,
    ) -> Booking | None:
        """
        Получение бронирования ID
        """
        booking = await self.booking_repository.get_by_id_and_user(
            booking_id=booking_id,
            session=session,
            user_id=user_id,
        )

        if booking is None:
            raise BookingNotFound()

        cancel_booking = await self.booking_repository.cancel_booking(
            booking=booking,
            session=session,
        )

        await session.commit()
        await session.refresh(booking)

        return cancel_booking
