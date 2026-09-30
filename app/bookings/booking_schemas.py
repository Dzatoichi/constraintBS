from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingCreate(BaseModel):
    room_id: int = Field(gt=0)
    check_in: date
    check_out: date
    guests: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self

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
