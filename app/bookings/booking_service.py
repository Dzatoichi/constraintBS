from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking
from app.bookings.booking_repository import BookingRepository
from app.bookings.booking_schemas import BookingCreate


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
        ) -> Booking | None:
            """
            Получение бронирования ID
            """
            booking = await self.booking_repository.get_by_id(
                obj_id=booking_id,
                session=session,
            )

            if booking is None:
                    # здесь позже своё domain exception
                    raise ValueError("Hotel not found")

            return booking


    async def get_bookings(
                    self,
                    session: AsyncSession,
            ) -> list[Booking] | None:
                """
                Получение бронирований
                """
                bookings = await self.booking_repository.get_all(
                    session=session,
                )
    
                if bookings is None:
                        # здесь позже своё domain exception
                        raise ValueError("Hotel not found")
    
                return bookings


    async def cancel_booking(
                    self,
                    booking_id: int,
                    session: AsyncSession,
            ) -> Booking | None:
                """
                Получение бронирования ID
                """
                booking = await self.booking_repository.get_by_id(
                    obj_id=booking_id,
                    session=session,
                )
    
                if booking is None:
                    # здесь позже своё domain exception
                    raise ValueError("Hotel not found")

                cancel_booking = await self.booking_repository.cancel_booking(
                       booking=booking,
                       session=session,
                )

                await session.commit()
                await session.refresh(booking)

    
                return cancel_booking