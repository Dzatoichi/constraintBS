from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from fastapi import Depends

from app.hotels.hotel_repository import HotelRepository
from app.shared.database import DatabaseHelper

from app.hotels.hotel_service import HotelService



AsyncSessionDep = Annotated[
    AsyncSession, 
    Depends(DatabaseHelper.session_getter)
]

