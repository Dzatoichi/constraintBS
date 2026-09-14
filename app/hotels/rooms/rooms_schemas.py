from pydantic import BaseModel, ConfigDict, Field

from app.hotels.rooms.rooms_model import RoomType

from datetime import datetime


class AmentityCreate(BaseModel):
    name: str


class AmentityRead(AmentityCreate):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
        )


class RoomCreate(BaseModel):
    number: str
    room_type: RoomType = Field(default=RoomType.STANDART)
    capacity: int
    price_per_night: int
    floor: int
    description: str | None = Field(default=None, max_length=500)

    amenities: list[AmentityRead] = Field(default_factory=list)


class RoomRead(RoomCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True
        )


class RoomUpdate(BaseModel):
    number: int | None 
    room_type: RoomType | None = Field(default=RoomType.STANDART)
    capacity: int | None
    price_per_night: int | None
    floor: int | None
    description: str | None = Field(default=None, max_length=500)
    amentity: list[int] | None


class RoomUpdateRead(RoomUpdate):
    id: int
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True
    )