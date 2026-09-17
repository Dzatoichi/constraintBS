from typing import Annotated

from fastapi import Depends

from app.users.users_repository import UsersRepository
from app.users.users_service import UsersService


def get_users_repository() -> UsersRepository:
    return UsersRepository()


UsersRepositoryDep = Annotated[UsersRepository, Depends(get_users_repository)]


def get_users_service(users_repository: UsersRepositoryDep) -> UsersService:
    return UsersService(users_repository=users_repository)


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]
