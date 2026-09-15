from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking, BookingStatus
from app.hotels.hotel_model import Hotel
from app.hotels.rooms.rooms_model import Room, RoomType
from app.hotels.rooms.rooms_schemas import RoomCreate, RoomUpdate
from app.shared.repository import BaseRepository


class RoomRepository(BaseRepository[
    Room,
    RoomCreate,
    RoomUpdate,
]):
    def __init__(self) -> None:
        super().__init__(Room)


    async def create(
            self,
            session: AsyncSession,
            hotel_id: int,
            data: RoomCreate,
    ) -> Room | None:
        """
        Переопределения метода create
        """
        room = self.model(**data.model_dump(), hotel_id=hotel_id)

        session.add(room)
        await session.flush()

        return room


    async def get_rooms_by_hotel(
            self,
            session: AsyncSession,
            hotel_id: int,
    ) -> list[Room] | None:
        """
        Все номера в отеле
        """
        stmt = select(self.model).where(self.model.hotel_id==hotel_id)
        rooms = await session.execute(stmt)

        return list(rooms.scalars().all())


    async def search_rooms(
            self,
            session: AsyncSession,
            city: str,
            check_in: date,
            check_out: date,
            guests: int,
            max_price: int | None,
            room_type: RoomType | None,
            amenities: list[int] | None,
    ) -> list[Room] | None:
        """
        Поиск комнат по параметрам
        """
        stmt = (
            select(Room)
            .join(Hotel, Room.hotel_id == Hotel.id)
            .where(
                Hotel.city == city,
                Room.capacity >= guests,
            )
        )

        if max_price is not None:
            stmt = stmt.where(
                Room.price_per_night <= max_price
            )

        if room_type is not None:
            stmt = stmt.where(
                Room.room_type == room_type
            )

        if amenities:
            for amenity in amenities:
                stmt = stmt.where(
                    Room.amenities.contains([amenity])
                )

        booking_exists = (
            select(Booking.id)
            .where(
                Booking.room_id == Room.id,
                Booking.status == BookingStatus.CONFIRMED,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .exists()
        )

        stmt = stmt.where(
            ~booking_exists
        )

        result = await session.execute(stmt)

        return list(result.scalars().all())


