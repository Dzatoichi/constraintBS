from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.hotels.rooms.rooms_model import RoomType


class AmentityCreate(BaseModel):
    name: str


class AmentityRead(AmentityCreate):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
        )


class RoomBase(BaseModel):
    number: str = Field(min_length=1, max_length=10)
    room_type: RoomType = Field(default=RoomType.STANDART)
    capacity: int = Field(gt=0)
    price_per_night: int = Field(ge=0)
    floor: int
    description: str | None = Field(default=None, max_length=500)

class RoomCreate(RoomBase):
    model_config = ConfigDict(extra="forbid")

    amenity_ids: list[int] = Field(default_factory=list)


class RoomRead(RoomBase):
    id: int
    amenities: list[AmentityRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoomUpdate(BaseModel):
    number: str | None =  None
    room_type: RoomType | None = Field(default=RoomType.STANDART)
    capacity: int | None = None
    price_per_night: int | None = None
    floor: int | None = None
    description: str | None = Field(default=None, max_length=500)
    amenities: list[int] | None = None


class RoomUpdateRead(RoomUpdate):
    id: int
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True
    )