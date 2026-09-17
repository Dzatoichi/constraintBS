from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth_schemas import RefreshTokenRequest, Token, UserRegister
from app.auth.dependencies import CurrentAccessTokenDep, CurrentUserDep
from app.auth.security import create_access_token, create_refresh_token, decode_token
from app.shared.dependecies import AsyncSessionDep
from app.users.dependencies import UsersServiceDep
from app.users.users_schemas import UserRead

auth_router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@auth_router.post(
    path="/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(
    data: UserRegister,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
) -> UserRead:
    user = await users_service.create_user(session=session, data=data)
    return UserRead.model_validate(user)


@auth_router.post(path="/login", response_model=Token, summary="Вход в систему")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
) -> Token:
    user = await users_service.authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_token_pair(user.id)


@auth_router.post(path="/refresh", response_model=Token, summary="Обновление пары токенов")
async def refresh(
    data: RefreshTokenRequest,
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
) -> Token:
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    try:
        user = await users_service.get_user(session=session, user_id=user_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token_pair(user_id)


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
)
async def logout(
    _: CurrentAccessTokenDep,
) -> None:
    """JWT is stateless, so the client must discard its tokens after this call."""


@auth_router.get(path="/me", response_model=UserRead, summary="Текущий пользователь")
async def get_me(current_user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(current_user)


def create_token_pair(user_id: int) -> Token:
    subject = str(user_id)
    return Token(
        access_token=create_access_token(subject=subject),
        refresh_token=create_refresh_token(subject=subject),
    )
