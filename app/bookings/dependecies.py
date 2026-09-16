from typing import Annotated

from fastapi import Depends

from app.bookings.booking_repository import BookingRepository
from app.bookings.booking_service import BookingService


def get_booking_repository() -> BookingRepository:
    return BookingRepository()


BookingRepositoryDep = Annotated[
    BookingRepository,
    Depends(get_booking_repository),
]


def get_booking_service(
        booking_repository: BookingRepositoryDep,
) -> BookingService:
    return BookingService(
        booking_repository=booking_repository,
    )


BookingServiceDep = Annotated[
    BookingService,
    Depends(get_booking_service)
]