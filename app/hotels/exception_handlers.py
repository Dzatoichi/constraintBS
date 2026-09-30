from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.hotels.errors import HotelNotFound


async def handle_hotel_not_found(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "hotel_not_found", "message": "Hotel not found"}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HotelNotFound, handle_hotel_not_found)
