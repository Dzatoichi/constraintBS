from sqlalchemy import select

from app.hotels.rooms.rooms_model import Room
from app.shared.repository import BaseRepository
from app.hotels.rooms.rooms_schemas import RoomCreate, RoomUpdate

from sqlalchemy.ext.asyncio import AsyncSession


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

