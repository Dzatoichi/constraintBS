from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    room_id: int
    check_in: date
    check_out: date
    guests: int


class BookingRead(BookingCreate):
    id: int
    user_id: int | None
    total_price: int
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True
    )

class BookingUpdate(BaseModel):
    room_id: int | None = None
    check_in: date | None = None
    check_out: date | None = None
    guests: int | None = None
