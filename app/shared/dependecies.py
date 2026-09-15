from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import db_helper

AsyncSessionDep = Annotated[
    AsyncSession, 
    Depends(db_helper.session_getter)
]

