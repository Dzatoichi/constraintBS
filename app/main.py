from fastapi import FastAPI

from app.hotels.hotel_router import hotel_router
from app.hotels.rooms.rooms_router import rooms_router

app = FastAPI(
    title="ConstraintBS",
    version="0.1.0",
)

app.include_router(hotel_router)
app.include_router(rooms_router)


@app.get("/health")
async def health():
    return {"status": "ok"}