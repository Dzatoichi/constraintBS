from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bookings.booking_model import Booking
from app.shared.repository import BaseRepository
from app.users.users_model import User


class UsersRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_bookings(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Booking]:
        result = await session.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())
