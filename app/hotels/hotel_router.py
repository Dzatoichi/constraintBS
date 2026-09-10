from fastapi import APIRouter

from app.hotels.hotel_schemas import HotelCreateResponse, HotelUpdateResponse, HotelCreate, HotelUpdate

from app.shared.dependecies import AsyncSessionDep

from app.hotels.dependencies import HotelServiceDep

hotel_router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)


@hotel_router.post(
        path="", 
        response_model=HotelCreateResponse,
        summary="Создание отеля",)
async def create_hotel(
    data: HotelCreate,
    session: AsyncSessionDep,
    hotel_service: HotelServiceDep,
) -> HotelCreateResponse:
    """
    Создание отеля
    """
    hotel = await hotel_service.create_hotel(session=session, data=data)

    return HotelCreateResponse.model_validate(hotel)

    
@hotel_router.get(
        path="",
        response_model=list[HotelCreateResponse],
        summary="Получение отелей"
        )
async def get_hotels(
    session: AsyncSessionDep,
    hotel_service: HotelServiceDep,
) -> list[HotelCreateResponse] | None:
    """
    Получение списка отелей
    """
    hotels = await hotel_service.get_hotels(session=session)

    if hotels is not None:
              return [
                   HotelCreateResponse.model_validate(hotel) for hotel in hotels
              ]

    return None
    

@hotel_router.get(
        path="/{hotel_id}",
        response_model=HotelCreateResponse,
        summary="Получение отеля по ID"
        )
async def get_hotel(
    hotel_id: int,
    session: AsyncSessionDep,
    hotel_service: HotelServiceDep,
) -> HotelCreateResponse:
    """
    Получение отеля по ID
    """
    hotel = await hotel_service.get_hotel(session=session, hotel_id=hotel_id)

    return HotelCreateResponse.model_validate(hotel)


@hotel_router.patch(
        path="/{hotel_id}",
        response_model=HotelUpdateResponse,
        summary="Обновление информации об отеле"
        )
async def update_hotel(
    hotel_id: int,
    data: HotelUpdate,
    session: AsyncSessionDep,
    hotel_service: HotelServiceDep,
) -> HotelUpdateResponse:
    """
    Обновление информации об отеле
    """
    hotel = await hotel_service.update_hotel(session=session, hotel_id=hotel_id, data=data)

    return HotelUpdateResponse.model_validate(hotel)