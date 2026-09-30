from fastapi import FastAPI

from app.auth.auth_router import auth_router
from app.bookings.booking_router import bookings_router
from app.bookings.exception_handlers import (
    register_exception_handlers as bookings_handlers,
)
from app.hotels.exception_handlers import register_exception_handlers as hotels_handlers
from app.hotels.hotel_router import hotel_router
from app.hotels.rooms.exception_handlers import (
    register_exception_handlers as hotels_rooms_handlers,
)
from app.hotels.rooms.rooms_router import rooms_router
from app.users.exception_handlers import register_exception_handlers as users_handlers
from app.users.users_router import users_router

app = FastAPI(
    title="ConstraintBS",
    version="0.1.0",
)

hotels_handlers(app)
hotels_rooms_handlers(app)
bookings_handlers(app)
users_handlers(app)

app.include_router(hotel_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
