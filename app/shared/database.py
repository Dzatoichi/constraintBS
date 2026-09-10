from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from collections.abc import AsyncGenerator

from app.shared.config import settings

class Base(DeclarativeBase):
    pass


class DatabaseHelper:
    def __init__(self):
        self.engine = create_async_engine(
            url = settings.CONNECT_ASYNC(),
            echo = False,
        )
        self.session_factory = async_sessionmaker(
            bind = self.engine,
            expire_on_commit = False,
        )

    async def session_getter(
            self,
        ) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session



