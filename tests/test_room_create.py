from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.hotels.rooms.rooms_model import Amenity
from app.hotels.rooms.rooms_repository import RoomRepository
from app.hotels.rooms.rooms_schemas import RoomCreate, RoomRead
from app.hotels.rooms.rooms_service import RoomsService
from app.users.users_model import User  # noqa: F401


def room_data(**fields):
    return RoomCreate(
        number="101", capacity=2, price_per_night=5000, floor=1, **fields
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("amenity_ids", [[], [1, 3], [1, 1, 3]])
async def test_create_room_with_existing_amenities(amenity_ids):
    session = AsyncMock(spec=AsyncSession)
    amenities = [Amenity(id=key, name=f"Amenity {key}") for key in sorted(set(amenity_ids))]
    session.scalars.return_value = Mock(all=Mock(return_value=amenities))
    service = RoomsService(RoomRepository())

    room = await service.create_room(
        session=session, hotel_id=10, data=room_data(amenity_ids=amenity_ids)
    )

    assert room.hotel_id == 10
    assert room.number == "101"
    assert room.amenities == amenities
    session.add.assert_called_once_with(room)
    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
    if not amenity_ids:
        session.scalars.assert_not_awaited()

    room.id = 42
    response = RoomRead.model_validate(room).model_dump()
    assert response["amenities"] == [
        {"id": item.id, "name": item.name} for item in amenities
    ]
    assert "amenity_ids" not in response


@pytest.mark.asyncio
async def test_unknown_amenities_do_not_create_room():
    session = AsyncMock(spec=AsyncSession)
    session.scalars.return_value = Mock(
        all=Mock(return_value=[Amenity(id=1, name="Wi-Fi")])
    )
    service = RoomsService(RoomRepository())

    with pytest.raises(HTTPException) as error:
        await service.create_room(
            session=session, hotel_id=10, data=room_data(amenity_ids=[1, 99])
        )

    assert error.value.status_code == 422
    assert error.value.detail["amenity_ids"] == [99]
    session.add.assert_not_called()
    session.flush.assert_not_awaited()
    session.commit.assert_not_awaited()


def test_omitted_amenities_default_to_empty():
    assert room_data().amenity_ids == []


def test_old_amenities_field_is_rejected():
    with pytest.raises(ValidationError):
        room_data(amenities=[1])
