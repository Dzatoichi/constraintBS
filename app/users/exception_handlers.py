from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.users.errors import EmailAlreadyExists, UsernameAlreadyExists, UserNotFound


async def handle_user_not_found(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "user_not_found", "message": "User not found"}},
    )


async def handle_email_already_exists(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "email_already_exists",
                "message": "A user with this email already exists",
            }
        },
    )


async def handle_username_already_exists(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "username_already_exists",
                "message": "A user with this username already exists",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFound, handle_user_not_found)
    app.add_exception_handler(EmailAlreadyExists, handle_email_already_exists)
    app.add_exception_handler(UsernameAlreadyExists, handle_username_already_exists)
