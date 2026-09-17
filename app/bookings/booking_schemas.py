from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingCreate(BaseModel):
    room_id: int
    check_in: date
    check_out: date
    guests: int
    guest_name: str
    guest_email: EmailStr


class BookingRead(BookingCreate):
    id: int
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
    guest_name: str | None = None
    guest_email: EmailStr | None = None
    