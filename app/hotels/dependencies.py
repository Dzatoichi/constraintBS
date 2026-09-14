from typing import Annotated

from fastapi import Depends

from app.hotels.hotel_repository import HotelRepository
from app.hotels.hotel_service import HotelService
from app.hotels.rooms.rooms_repository import RoomRepository
from app.hotels.rooms.rooms_service import RoomsService


def get_hotel_repository() -> HotelRepository:
    return HotelRepository()


def get_room_repository() -> RoomRepository:
    return RoomRepository()


HotelRepositoryDep = Annotated[
    HotelRepository,
    Depends(get_hotel_repository),
]


RoomRepositoryDep = Annotated[
    RoomRepository,
    Depends(get_room_repository),
]


def get_hotel_service(
    hotel_repository: HotelRepositoryDep,
) -> HotelService:
    return HotelService(
        hotel_repository=hotel_repository,
    )


def get_room_service(
        room_repository: RoomRepositoryDep,
) -> RoomsService:
    return RoomsService(
        rooms_repository=room_repository,
    )
    

RoomServiceDep = Annotated[
    RoomsService,
    Depends(get_room_service),
]


HotelServiceDep = Annotated[
    HotelService,
    Depends(get_hotel_service),
]


