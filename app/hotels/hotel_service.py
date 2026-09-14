from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.hotel_model import Hotel
from app.hotels.hotel_repository import HotelRepository

from app.hotels.hotel_schemas import HotelCreate, HotelUpdate

class HotelService:
    def __init__(self, hotel_repository: HotelRepository):
         self.hotel_repository = hotel_repository

    async def create_hotel(
            self,
            session: AsyncSession,
            data: HotelCreate
    ) -> Hotel | None:
         """
         Создание отеля
         """
         hotel = await self.hotel_repository.create(
             session = session,
             data = data,
        )
         await session.commit()
         await session.refresh(hotel)

         return hotel

    async def get_hotels(
              self,
              session: AsyncSession,
    ) -> list[Hotel] | None:
         """
         Получение отелей
         """
         hotels = await self.hotel_repository.get_all(
              session = session,
         )

         return hotels

    async def get_hotel(
              self,
              hotel_id: int,
              session: AsyncSession
    ) -> Hotel:
         """
         Получение отеля по id
         """
         hotel = await self.hotel_repository.get_by_id(
              session = session, 
              obj_id = hotel_id,
         )
         if hotel is None:
            # здесь позже своё domain exception
            raise ValueError("Hotel not found")

         return hotel

    async def update_hotel(
              self,
              hotel_id: int,
              data: HotelUpdate,
              session: AsyncSession,
    ) -> Hotel:
         """
         Обновление отеля
         """
         hotel = await self.hotel_repository.get_by_id(
            session=session,
            obj_id=hotel_id,
        )

         if hotel is None:
            raise ValueError("Hotel not found")

         updated_hotel = await self.hotel_repository.update(
              data = data,
              obj = hotel,
              session = session,
         )
         await session.commit()
         await session.refresh(updated_hotel)

         return updated_hotel

    async def delete_hotel(
            self,
            hotel_id: int,
            session: AsyncSession,
    ) -> None:
        """
        Удаления отеля
        """
        del_hotel = await self.hotel_repository.get_by_id(
            obj_id=hotel_id,
            session=session,
        )

        if del_hotel is None:
            raise ValueError("Hotel not found")

        result = await self.hotel_repository.delete(
            obj=del_hotel,
            session=session,
        )
        await session.commit()

        return result