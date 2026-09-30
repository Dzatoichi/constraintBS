from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, create_refresh_token
from app.bookings.errors import BookingConflict, BookingNotFound, InvalidBookingDates
from app.hotels.errors import HotelNotFound
from app.hotels.rooms.errors import (
    InvalidSearchDates,
    RoomCapacityExceeded,
    RoomNotFound,
    UnknownAmenities,
)
from app.main import app
from app.shared.database import db_helper
from app.users.dependencies import get_users_service
from app.users.errors import EmailAlreadyExists, UsernameAlreadyExists, UserNotFound


@pytest.mark.parametrize(
    "error,status,code",
    [
        (HotelNotFound(), 404, "hotel_not_found"),
        (RoomNotFound(), 404, "room_not_found"),
        (RoomCapacityExceeded(), 422, "room_capacity_exceeded"),
        (InvalidSearchDates(), 422, "invalid_search_dates"),
        (UnknownAmenities([99]), 422, "unknown_amenities"),
        (BookingNotFound(), 404, "booking_not_found"),
        (BookingConflict(), 409, "booking_conflict"),
        (InvalidBookingDates(), 422, "invalid_booking_dates"),
        (UserNotFound(), 404, "user_not_found"),
        (EmailAlreadyExists(), 409, "email_already_exists"),
        (UsernameAlreadyExists(), 409, "username_already_exists"),
    ],
)
def test_registered_domain_handlers(error, status, code):
    test_app = FastAPI(exception_handlers=app.exception_handlers)

    @test_app.get("/failure")
    async def failure():
        raise error

    with TestClient(test_app) as client:
        response = client.get("/failure")
    assert response.status_code == status
    payload = response.json()["error"]
    assert payload["code"] == code
    assert payload["message"]
    if isinstance(error, UnknownAmenities):
        assert payload["details"] == {"amenity_ids": [99]}


@pytest.mark.parametrize("token_type", ["access", "refresh"])
def test_deleted_user_still_returns_401(token_type):
    service = Mock(get_user=AsyncMock(side_effect=UserNotFound()))

    async def session_override():
        yield Mock()

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_users_service] = lambda: service
    app.dependency_overrides[db_helper.session_getter] = session_override
    try:
        with TestClient(app) as client:
            if token_type == "access":
                token = create_access_token("123")
                response = client.get(
                    "/auth/me", headers={"Authorization": f"Bearer {token}"}
                )
            else:
                response = client.post(
                    "/auth/refresh", json={"refresh_token": create_refresh_token("123")}
                )
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def test_unexpected_error_is_not_converted_to_client_error():
    test_app = FastAPI(exception_handlers=app.exception_handlers)

    @test_app.get("/failure")
    async def failure():
        raise ValueError("internal database secret")

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/failure")
    assert response.status_code == 500
    assert "internal database secret" not in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "room,conflict,error",
    [
        (None, False, RoomNotFound),
        (Mock(capacity=1), False, RoomCapacityExceeded),
        (Mock(capacity=2), True, BookingConflict),
    ],
)
async def test_booking_service_rejects_before_writing(room, conflict, error):
    from app.bookings.booking_schemas import BookingCreate
    from app.bookings.booking_service import BookingService

    repository = Mock(
        get_room=AsyncMock(return_value=room),
        has_conflict=AsyncMock(return_value=conflict),
        create=AsyncMock(),
    )
    session = AsyncMock()
    data = BookingCreate(
        room_id=1, check_in="2026-10-01", check_out="2026-10-02", guests=2
    )
    with pytest.raises(error):
        await BookingService(repository).create_booking(session, data, Mock())
    repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "changes",
    [
        {"guests": 0},
        {"room_id": 0},
        {"check_out": "2026-10-01"},
    ],
)
def test_invalid_booking_input(changes):
    from pydantic import ValidationError

    from app.bookings.booking_schemas import BookingCreate

    payload = {"room_id": 1, "check_in": "2026-10-01", "check_out": "2026-10-02", "guests": 2}
    payload.update(changes)
    with pytest.raises(ValidationError):
        BookingCreate(**payload)
