from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.rooms.rooms_repository import RoomRepository

from app.hotels.rooms.rooms_model import Room

from app.hotels.rooms.rooms_schemas import RoomCreate, RoomUpdate



class RoomsService:
    def __init__(self, rooms_repository: RoomRepository):
        self.rooms_repository = rooms_repository

    async def create_room(
            self,
            session: AsyncSession,
            hotel_id: int,
            data: RoomCreate,
    ) -> Room | None:
        """
        Создание комнаты
        """
        room = await self.rooms_repository.create(
            session=session,
            data=data,
            hotel_id=hotel_id,
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

        if rooms is None:
            raise ValueError("Not found")

        return rooms


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
            raise ValueError("Room not found")

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
            raise ValueError("Room not found")

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
            raise ValueError("Room not found")

        updated_room = await self.rooms_repository.update(
            data=data,
            obj = room,
            session=session,
        )
        await session.commit()
        await session.refresh(updated_room)

        return updated_room 
        
