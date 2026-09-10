from sqlalchemy import text

from fastapi import Depends, FastAPI

from app.hotels.hotel_router import hotel_router
from app.shared.database import DatabaseHelper

app = FastAPI(
    title="ConstraintBS",
    version="0.1.0",
)

app.include_router(hotel_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db(
    session = Depends(DatabaseHelper().session_getter)
    ):
    result = await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": result.scalar_one()}