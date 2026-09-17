from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_password_hash, verify_password
from app.bookings.booking_model import Booking
from app.users.users_model import User
from app.users.users_repository import UsersRepository
from app.users.users_schemas import UserCreate, UserUpdate


class UsersService:
    def __init__(self, users_repository: UsersRepository) -> None:
        self.users_repository = users_repository

    async def create_user(self, session: AsyncSession, data: UserCreate) -> User | None:
        await self._ensure_unique_user_fields(
            session=session,
            email=data.email,
            username=data.username,
        )

        user = await self.users_repository.create(
            session=session,
            payload={
                "email": str(data.email),
                "username": data.username,
                "full_name": data.full_name,
                "password_hash": get_password_hash(data.password),
            },
        )
        await session.commit()
        await session.refresh(user)
        return user

    async def get_user(self, session: AsyncSession, user_id: int) -> User:
        user = await self.users_repository.get_by_id(session=session, obj_id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def get_users(self, session: AsyncSession) -> list[User]:
        return await self.users_repository.get_all(session=session) or []

    async def authenticate_user(
        self,
        session: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        user = await self.users_repository.get_by_email(session=session, email=email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user

    async def update_user(
        self,
        session: AsyncSession,
        user_id: int,
        data: UserUpdate,
    ) -> User:
        user = await self.get_user(session=session, user_id=user_id)
        payload = data.model_dump(exclude_unset=True)

        email = payload.get("email")
        if email is not None and str(email) != user.email:
            await self._ensure_email_is_available(session=session, email=str(email))
            payload["email"] = str(email)

        username = payload.get("username")
        if username is not None and username != user.username:
            await self._ensure_username_is_available(session=session, username=username)

        password = payload.pop("password", None)
        if password is not None:
            payload["password_hash"] = get_password_hash(password)

        updated_user = await self.users_repository.update(
            session=session,
            obj=user,
            update_payload=payload,
        )
        await session.commit()
        await session.refresh(updated_user)
        return updated_user

    async def delete_user(self, session: AsyncSession, user_id: int) -> None:
        user = await self.get_user(session=session, user_id=user_id)
        await self.users_repository.delete(session=session, obj=user)
        await session.commit()

    async def get_user_bookings(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Booking]:
        await self.get_user(session=session, user_id=user_id)
        return await self.users_repository.get_bookings(session=session, user_id=user_id)

    async def _ensure_unique_user_fields(
        self,
        session: AsyncSession,
        email: str,
        username: str,
    ) -> None:
        await self._ensure_email_is_available(session=session, email=email)
        await self._ensure_username_is_available(session=session, username=username)

    async def _ensure_email_is_available(self, session: AsyncSession, email: str) -> None:
        if await self.users_repository.get_by_email(session=session, email=email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

    async def _ensure_username_is_available(
        self,
        session: AsyncSession,
        username: str,
    ) -> None:
        if await self.users_repository.get_by_username(session=session, username=username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this username already exists",
            )
