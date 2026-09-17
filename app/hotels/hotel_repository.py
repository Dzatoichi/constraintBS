from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.hotel_model import Hotel
from app.shared.repository import BaseRepository


class HotelRepository(BaseRepository[
    Hotel,
    ]):

    def __init__(self) -> None:
        super().__init__(Hotel)

    async def get_by_city(
            self,
            session: AsyncSession,
            city: str,
    ) -> list[Hotel] | None :

        stmt = select(Hotel).where(Hotel.city == city)

        hotels = await session.execute(stmt)

        return list(hotels.scalars().all())