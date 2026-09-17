from pydantic import BaseModel

from app.users.users_schemas import UserCreate


class UserRegister(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenPayload(BaseModel):
    user_id: int
