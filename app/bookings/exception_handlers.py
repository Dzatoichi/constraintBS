from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.bookings.errors import BookingConflict, BookingNotFound, InvalidBookingDates


async def handle_booking_not_found(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {"code": "booking_not_found", "message": "Booking not found"}
        },
    )


async def handle_booking_conflict(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "booking_conflict",
                "message": "Room is already booked for these dates",
            }
        },
    )


async def handle_invalid_booking_dates(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_booking_dates",
                "message": "check_out must be after check_in",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BookingNotFound, handle_booking_not_found)
    app.add_exception_handler(BookingConflict, handle_booking_conflict)
    app.add_exception_handler(InvalidBookingDates, handle_invalid_booking_dates)
