from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.rooms.errors import InvalidSearchDates, RoomNotFound, UnknownAmenities
from app.hotels.rooms.rooms_model import Room, RoomType
from app.hotels.rooms.rooms_repository import RoomRepository
from app.hotels.rooms.rooms_schemas import RoomCreate, RoomUpdate


class RoomsService:
    def __init__(self, rooms_repository: RoomRepository):
        self.rooms_repository = rooms_repository

    async def create_room(
            self,
            session: AsyncSession,
            hotel_id: int,
            data: RoomCreate,
    ) -> Room:
        """
        Создание комнаты
        """
        amenities = await self.rooms_repository.get_amenities(
            session=session,
            amenity_ids=data.amenity_ids,
        )
        missing_ids = set(data.amenity_ids) - {amenity.id for amenity in amenities}
        if missing_ids:
            raise UnknownAmenities(sorted(missing_ids))

        room = await self.rooms_repository.create(
            session=session,
            data=data,
            hotel_id=hotel_id,
            amenities=amenities,
        )
        await session.commit()
        await session.refresh(room)

        return room


    async def get_rooms(
            self,
            session: AsyncSession,
            hotel_id: int,
    ) -> list[Room] | None:
        """
        Список номеров
        """
        rooms = await self.rooms_repository.get_rooms_by_hotel(
            session=session,
            hotel_id=hotel_id,
        )

        return rooms or []


    async def get_room(
            self,
            session: AsyncSession,
            room_id: int,
    ) -> Room | None:
        """
        Получение номера по id
        """
        room = await self.rooms_repository.get_by_id(
            session=session,
            obj_id=room_id,
        )

        if room is None:
            raise RoomNotFound()

        return room


    async def delete_room(
            self,
            session: AsyncSession,
            room_id: int,
    ) -> None:
        """
        Удаление номера по id
        """
        room = await self.rooms_repository.get_by_id(
            session=session,
            obj_id=room_id,
        )

        if room is None:
            raise RoomNotFound()

        result = await self.rooms_repository.delete(
            session=session,
            obj=room,
        )
        await session.commit()

        return result


    async def update_room(
            self,
            session: AsyncSession,
            room_id: int,
            data: RoomUpdate,
    ) -> Room:
        """
        Обновление номера по id
        """
        room = await self.rooms_repository.get_by_id(
            session=session,
            obj_id=room_id,
        )

        if room is None:
            raise RoomNotFound()

        upd_payload = data.model_dump(exclude_none=True)

        updated_room = await self.rooms_repository.update(
            update_payload=upd_payload,
            obj = room,
            session=session,
        )
        await session.commit()
        await session.refresh(updated_room)

        return updated_room 


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
        Поиск номеров по параметрам
        """
        if check_in >= check_out:
            raise InvalidSearchDates()

        rooms = await self.rooms_repository.search_rooms(
            session=session,
            city=city,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            max_price=max_price,
            room_type=room_type,
            amenities=amenities,
        )

        return rooms or []


        
