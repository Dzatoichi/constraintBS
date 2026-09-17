from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.auth_schemas import AccessTokenPayload
from app.auth.security import decode_token
from app.shared.dependecies import AsyncSessionDep
from app.users.dependencies import UsersServiceDep
from app.users.users_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_access_token(
    session: AsyncSessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AccessTokenPayload:
    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if payload.get("type") != "access" or not isinstance(subject, str):
            raise credentials_exception
        user_id = int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception from None

    return AccessTokenPayload(user_id=user_id)


CurrentAccessTokenDep = Annotated[AccessTokenPayload, Depends(get_current_access_token)]


async def get_current_user(
    session: AsyncSessionDep,
    users_service: UsersServiceDep,
    access_token: CurrentAccessTokenDep,
) -> User:

    try:
        user = await users_service.get_user(
            session=session,
            user_id=access_token.user_id,
        )
    except HTTPException as error:
        if error.status_code == status.HTTP_404_NOT_FOUND:
            raise credentials_exception from None
        raise

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
