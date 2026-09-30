from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.hotels.rooms.errors import (
    InvalidSearchDates,
    RoomCapacityExceeded,
    RoomNotFound,
    UnknownAmenities,
)


async def handle_room_not_found(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "room_not_found", "message": "Room not found"}},
    )


async def handle_room_capacity_exceeded(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "room_capacity_exceeded",
                "message": "Room capacity is insufficient",
            }
        },
    )


async def handle_invalid_search_dates(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_search_dates",
                "message": "check_out must be after check_in",
            }
        },
    )


async def handle_unknown_amenities(
    request: Request, exc: Exception
) -> JSONResponse:
    if not isinstance(exc, UnknownAmenities):
        raise exc

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "unknown_amenities",
                "message": "Unknown amenity IDs",
                "details": {"amenity_ids": exc.amenity_ids},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RoomNotFound, handle_room_not_found)
    app.add_exception_handler(RoomCapacityExceeded, handle_room_capacity_exceeded)
    app.add_exception_handler(InvalidSearchDates, handle_invalid_search_dates)
    app.add_exception_handler(UnknownAmenities, handle_unknown_amenities)
