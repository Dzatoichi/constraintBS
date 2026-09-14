from fastapi import APIRouter

from app.hotels.rooms.rooms_schemas import RoomRead, RoomCreate, RoomUpdate, RoomUpdateRead

from app.hotels.dependencies import RoomServiceDep

from app.shared.dependecies import AsyncSessionDep


rooms_router = APIRouter(
    tags=["Номера"]
)

@rooms_router.post(
    path="/hotels/{hotel_id}/rooms",
    response_model=RoomRead,
    summary="Создание номера в отеле",
)
async def create_room(
    data: RoomCreate,
    hotel_id: int,
    session: AsyncSessionDep,
    rooms_service: RoomServiceDep,
) -> RoomRead:
    """
    Создание номера в отеле
    """
    room = await rooms_service.create_room(
        session=session,
        hotel_id=hotel_id,
        data=data
    )

    return RoomRead.model_validate(room)


@rooms_router.get(
    path="/hotels/{hotel_id}/rooms",
    response_model=list[RoomRead],
    summary="Получение номеров в отеле",
)
async def get_rooms_for_hotel(
    hotel_id: int,
    session: AsyncSessionDep,
    rooms_service: RoomServiceDep,
) -> list[RoomRead] | None:
    """
    Получение списка номеров отеля
    """

    rooms = await rooms_service.get_rooms(
        session=session,
        hotel_id=hotel_id,
    )

    if rooms is not None:
        return [
            RoomRead.model_validate(room) 
            for room in rooms
            ]


@rooms_router.get(
    path="/rooms/{room_id}",
    response_model=RoomRead,
    summary="Получение номера в отеле по id"
)
async def get_room_by_id(
    room_id: int,
    session: AsyncSessionDep, 
    rooms_service: RoomServiceDep,
) -> RoomRead:
    """
    Получение номера в отеле по id
    """

    room = await rooms_service.get_room(
        session=session,
        room_id=room_id,
    )

    return RoomRead.model_validate(room)


@rooms_router.patch(
    path="/rooms/{room_id}",
    response_model=RoomUpdateRead,
    summary="Обновление данных номера в отеле"
)
async def update_room(
    room_id: int,
    data: RoomUpdate,
    session: AsyncSessionDep,
    room_service: RoomServiceDep,
) -> RoomUpdateRead:
    """
    Обновление данных номера в отеле
    """
    room = await room_service.update_room(
        session=session,
        data=data,
        room_id=room_id,
    )

    return RoomUpdateRead.model_validate(room)


@rooms_router.delete(
    path="/rooms/{room_id}",
    response_model=None,
    summary="Удаление номера"
)
async def delete_room(
    room_id: int,
    session: AsyncSessionDep, 
    rooms_service: RoomServiceDep,
) -> None:
    """
    Удаление номера
    """

    result = await rooms_service.delete_room(
        session=session,
        room_id=room_id,
    )

    return result