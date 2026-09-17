from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUserDep
from app.bookings.booking_schemas import BookingRead
from app.shared.dependecies import AsyncSessionDep
from app.users.dependencies import UsersServiceDep
from app.users.users_schemas import UserRead, UserUpdate

users_router = APIRouter(tags=["Пользователи"], prefix="/users")


def ensure_user_access(requested_user_id: int, current_user_id: int) -> None:
    if requested_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user data",
        )


@users_router.get(
    path="/me",
    response_model=UserRead,
    summary="Получение своего профиля",
)
async def get_current_user(current_user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(current_user)


@users_router.get(
    path="/me/bookings",
    response_model=list[BookingRead],
    summary="Получение своих бронирований",
)
async def get_current_user_bookings(
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> list[BookingRead]:
    bookings = await users_service.get_user_bookings(
        session=session,
        user_id=current_user.id,
    )
    return [BookingRead.model_validate(booking) for booking in bookings]


@users_router.get(
    path="/{user_id}/bookings",
    response_model=list[BookingRead],
    summary="Получение бронирований пользователя",
)
async def get_user_bookings(
    user_id: int,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> list[BookingRead]:
    ensure_user_access(user_id, current_user.id)
    bookings = await users_service.get_user_bookings(
        session=session,
        user_id=user_id,
    )
    return [BookingRead.model_validate(booking) for booking in bookings]


@users_router.get(
    path="/{user_id}",
    response_model=UserRead,
    summary="Получение пользователя по ID",
)
async def get_user(
    user_id: int,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> UserRead:
    ensure_user_access(user_id, current_user.id)
    user = await users_service.get_user(session=session, user_id=user_id)
    return UserRead.model_validate(user)


@users_router.get(
    path="",
    response_model=list[UserRead],
    summary="Получение списка пользователей",
)
async def get_users(
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    _: CurrentUserDep,
) -> list[UserRead]:
    users = await users_service.get_users(session=session)
    return [UserRead.model_validate(user) for user in users]


@users_router.patch(
    path="/{user_id}",
    response_model=UserRead,
    summary="Обновление данных пользователя",
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> UserRead:
    ensure_user_access(user_id, current_user.id)
    updated_user = await users_service.update_user(
        session=session,
        user_id=user_id,
        data=data,
    )
    return UserRead.model_validate(updated_user)


@users_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
)
async def delete_user(
    user_id: int,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> None:
    ensure_user_access(user_id, current_user.id)
    await users_service.delete_user(session=session, user_id=user_id)
