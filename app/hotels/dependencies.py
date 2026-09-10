from typing import Annotated

from fastapi import Depends

from app.hotels.hotel_repository import HotelRepository
from app.hotels.hotel_service import HotelService


def get_hotel_repository() -> HotelRepository:
    return HotelRepository()


HotelRepositoryDep = Annotated[
    HotelRepository,
    Depends(get_hotel_repository),
]


def get_hotel_service(
    hotel_repository: HotelRepositoryDep,
) -> HotelService:
    return HotelService(
        hotel_repository=hotel_repository,
    )


HotelServiceDep = Annotated[
    HotelService,
    Depends(get_hotel_service),
]