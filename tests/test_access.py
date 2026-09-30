from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, create_refresh_token
from app.bookings.booking_service import BookingService
from app.bookings.dependecies import get_booking_service
from app.bookings.errors import BookingNotFound
from app.hotels.dependencies import get_hotel_service, get_room_service
from app.main import app
from app.shared.database import db_helper
from app.users.dependencies import get_users_service

HOTEL = {"name": "Test hotel", "country": "RU", "city": "Test", "address": "Test"}
ROOM = {"number": "101", "capacity": 2, "price_per_night": 1000, "floor": 1}
ADMIN_ROUTES = [
    ("GET", "/users", None),
    ("GET", "/bookings", None),
    ("GET", "/bookings/1", None),
    ("POST", "/hotels", HOTEL),
    ("PATCH", "/hotels/1", {"name": "Changed hotel"}),
    ("DELETE", "/hotels/1", None),
    ("POST", "/hotels/1/rooms", ROOM),
    ("PATCH", "/rooms/1", {"number": "102"}),
    ("DELETE", "/rooms/1", None),
]


@pytest.fixture
def api():
    user = SimpleNamespace(
        id=7,
        email="user@example.com",
        username="user",
        full_name="Test",
        is_active=True,
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=None,
    )
    users = Mock(
        get_user=AsyncMock(return_value=user),
        get_users=AsyncMock(return_value=[]),
        get_user_bookings=AsyncMock(return_value=[]),
    )
    hotels = Mock(
        create_hotel=AsyncMock(return_value={"id": 1, **HOTEL}),
        get_hotels=AsyncMock(return_value=[]),
    )
    rooms = Mock(search_rooms=AsyncMock(return_value=[]))
    bookings = Mock(get_bookings=AsyncMock(return_value=[]))
    session = AsyncMock()

    async def session_override():
        yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides.update(
        {
            db_helper.session_getter: session_override,
            get_users_service: lambda: users,
            get_hotel_service: lambda: hotels,
            get_room_service: lambda: rooms,
            get_booking_service: lambda: bookings,
        }
    )
    try:
        with TestClient(app) as client:
            yield SimpleNamespace(
                client=client,
                user=user,
                users=users,
                hotels=hotels,
                rooms=rooms,
                bookings=bookings,
                headers={"Authorization": f"Bearer {create_access_token('7')}"},
            )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.parametrize("method,path,payload", ADMIN_ROUTES)
@pytest.mark.parametrize("authenticated", [False, True])
def test_admin_routes_reject_unauthorized_users(
    api, method, path, payload, authenticated
):
    response = api.client.request(
        method, path, json=payload, headers=api.headers if authenticated else {}
    )
    assert response.status_code == (403 if authenticated else 401)
    # Domain operations must never be reached on rejected requests.
    for service in (api.hotels, api.rooms, api.bookings):
        assert service.mock_calls == []
    api.users.get_users.assert_not_awaited()


def test_admin_can_create_hotel(api):
    api.user.is_admin = True
    response = api.client.post("/hotels", json=HOTEL, headers=api.headers)
    assert response.status_code in (200, 201)
    assert response.json()["name"] == HOTEL["name"]
    api.hotels.create_hotel.assert_awaited_once()


@pytest.mark.parametrize("path", ["/users", "/bookings"])
def test_admin_can_read_admin_lists(api, path):
    api.user.is_admin = True
    response = api.client.get(path, headers=api.headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("path", ["/users/8", "/users/8/bookings"])
def test_cannot_read_another_user(api, path):
    response = api.client.get(path, headers=api.headers)
    assert response.status_code == 403
    api.users.get_user_bookings.assert_not_awaited()


def test_my_bookings_uses_authenticated_user_id(api):
    response = api.client.get("/users/me/bookings", headers=api.headers)
    assert response.status_code == 200
    assert api.users.get_user_bookings.await_args.kwargs["user_id"] == 7


@pytest.mark.parametrize(
    "token",
    [
        "invalid",
        create_refresh_token("7"),
        create_access_token("7", timedelta(seconds=-1)),
    ],
)
def test_invalid_tokens_are_rejected(api, token):
    response = api.client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    api.users.get_user.assert_not_awaited()


def test_inactive_user_is_rejected(api):
    api.user.is_active = False
    assert api.client.get("/auth/me", headers=api.headers).status_code == 403


def test_public_search_needs_no_token(api):
    response = api.client.get(
        "/rooms/search",
        params={
            "city": "Test",
            "check_in": "2026-10-01",
            "check_out": "2026-10-02",
            "guests": 1,
        },
    )
    assert response.status_code == 200
    api.users.get_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_cannot_cancel_another_users_booking():
    repository = Mock(
        get_by_id_and_user=AsyncMock(return_value=None), cancel_booking=AsyncMock()
    )
    session = AsyncMock()
    with pytest.raises(BookingNotFound):
        await BookingService(repository).cancel_booking(
            booking_id=123, session=session, user_id=7
        )
    assert repository.get_by_id_and_user.await_args.kwargs["user_id"] == 7
    repository.cancel_booking.assert_not_awaited()
    session.commit.assert_not_awaited()
