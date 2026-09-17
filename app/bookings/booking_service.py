from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking
from app.bookings.booking_repository import BookingRepository
from app.bookings.booking_schemas import BookingCreate
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
        await self.booking_repository.validate_booking(
               session=session,
               room_id=data.room_id,
               check_in=data.check_in,
               check_out=data.check_out,
               guests=data.guests
               )

        total_price = await self.booking_repository.calculate_total_price(
               session=session,
               room_id=data.room_id,
               check_in=data.check_in,
               check_out=data.check_out,
               )
               
        payload = data.model_dump()

        payload["total_price"] = total_price
        payload["user_id"] = user.id
        payload["guest_name"] = user.full_name or user.username
        payload["guest_email"] = user.email

        booking = await self.booking_repository.create(
            payload=payload,
            session=session,
        )

        await session.commit()
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
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Booking not found",
                    )

            return booking


    async def get_bookings(
                    self,
                    session: AsyncSession,
            ) -> list[Booking]:
                """
                Получение бронирований
                """
                return await self.booking_repository.get_all(
                    session=session,
                ) or []


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
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Booking not found",
                    )

                cancel_booking = await self.booking_repository.cancel_booking(
                       booking=booking,
                       session=session,
                )

                await session.commit()
                await session.refresh(booking)

    
                return cancel_booking
