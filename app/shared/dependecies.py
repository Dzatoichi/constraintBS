from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from fastapi import Depends

from app.shared.database import db_helper



AsyncSessionDep = Annotated[
    AsyncSession, 
    Depends(db_helper.session_getter)
]

