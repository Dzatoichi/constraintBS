from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime

class HotelCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    country: str = Field(max_length=30)
    city: str  = Field(max_length=30)
    address: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)


class HotelCreateResponse(HotelCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
    ) 


class HotelUpdate(BaseModel):
    name: str | None = Field(default=None,min_length=3, max_length=30)
    country: str | None = Field(default=None,max_length=30)
    city: str | None  = Field(default=None,max_length=30)
    address: str | None = Field(default=None,max_length=100)
    description: str | None = Field(default=None, max_length=500)


class HotelUpdateResponse(HotelCreateResponse):
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
    )