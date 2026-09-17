from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep
from app.bookings.booking_schemas import BookingCreate, BookingRead
from app.bookings.dependecies import BookingServiceDep
from app.shared.dependecies import AsyncSessionDep

bookings_router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"]
)

@bookings_router.post(
    path="",
    response_model=BookingRead,
    summary="Создания бронирования"
)
async def create_booking(
    data: BookingCreate,
    session: AsyncSessionDep,
    bookings_service: BookingServiceDep,
    current_user: CurrentUserDep,
) -> BookingRead:
    """
    Создание бронирования
    """
    booking = await bookings_service.create_booking(
        session=session,
        data=data,
        user=current_user,
    )

    return BookingRead.model_validate(booking)


@bookings_router.get(
    path="/{booking_id}",
    response_model=BookingRead,
    summary="Получение бронирования по ID"
)
async def get_booking(
    booking_id: int,
    session: AsyncSessionDep,
    bookings_service: BookingServiceDep,
) -> BookingRead:
    """
    Получение бронирования по ID
    """
    booking = await bookings_service.get_booking(
        session=session,
        booking_id=booking_id,
    )

    return BookingRead.model_validate(booking)


@bookings_router.get(
    path="",
    response_model=list[BookingRead],
    summary="Получения списка бронирований"
)
async def get_bookings(
    session: AsyncSessionDep,
    bookings_service: BookingServiceDep,
) -> list[BookingRead] | None:
    """
    Получение бронирований
    """
    bookings = await bookings_service.get_bookings(
        session=session,
    )

    if bookings is not None: 
        return [BookingRead.model_validate(booking) for booking in bookings]


@bookings_router.patch(
    path="/{booking_id}/cancel",
    response_model=BookingRead,
    summary="Отмена бронирования"
)
async def cancel_booking(
    booking_id: int,
    session: AsyncSessionDep,
    bookings_service: BookingServiceDep,
    current_user: CurrentUserDep,
) -> BookingRead:
    """
    Отмена бронирования
    """
    booking = await bookings_service.cancel_booking(
        session=session,
        booking_id=booking_id,
        user_id=current_user.id,
    )

    return BookingRead.model_validate(booking)
