"""Run with TEST_DATABASE_NAME=constraintbs_test_... after alembic upgrade head."""

import asyncio
import os
from datetime import date
from types import SimpleNamespace

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import func, insert, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.bookings.booking_model import Booking
from app.bookings.booking_repository import BookingRepository
from app.bookings.booking_service import BookingService
from app.bookings.dependecies import get_booking_service
from app.hotels.hotel_model import Hotel
from app.hotels.rooms.rooms_model import Room
from app.main import app
from app.shared.config import settings
from app.shared.database import db_helper
from app.users.users_model import User

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def database():
    name = os.getenv("TEST_DATABASE_NAME")
    if not name:
        if os.getenv("CI") == "true":
            pytest.fail("TEST_DATABASE_NAME is required in CI")
        pytest.skip(
            "Set TEST_DATABASE_NAME to an isolated migrated PostgreSQL database"
        )
    if not name.startswith("constraintbs_test_") or name == settings.DB_NAME:
        pytest.fail("Refusing to clear a non-test database")
    engine = create_async_engine(make_url(settings.CONNECT_ASYNC()).set(database=name))
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "TRUNCATE bookings, room_amenity, rooms, hotels, users RESTART IDENTITY CASCADE"
                )
            )
            await conn.execute(
                insert(Hotel.__table__).values(
                    id=1, name="Test", country="RU", city="Test", address="Test"
                )
            )
            await conn.execute(
                insert(Room.__table__),
                [
                    {
                        "id": i,
                        "hotel_id": 1,
                        "number": str(i),
                        "capacity": 2,
                        "floor": 1,
                        "price_per_night": 1000,
                    }
                    for i in (1, 2)
                ],
            )
            await conn.execute(
                insert(User.__table__).values(
                    id=1,
                    email="test@example.com",
                    username="test",
                    password_hash="unused",
                )
            )
        yield engine
    finally:
        await engine.dispose()


def booking(**changes):
    payload = {
        "room_id": 1,
        "user_id": 1,
        "check_in": date(2026, 10, 1),
        "check_out": date(2026, 10, 3),
        "guests": 1,
        "guest_name": "Test",
        "guest_email": "test@example.com",
        "total_price": 2000,
    }
    payload.update(changes)
    return payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "second,allowed",
    [
        ({}, False),
        ({"room_id": 2}, True),
        ({"check_in": date(2026, 10, 3), "check_out": date(2026, 10, 5)}, True),
    ],
)
async def test_database_overlap_constraint(database, second, allowed):
    async with database.begin() as conn:
        await conn.execute(insert(Booking.__table__).values(**booking()))
    if allowed:
        async with database.begin() as conn:
            await conn.execute(insert(Booking.__table__).values(**booking(**second)))
    else:
        with pytest.raises(IntegrityError) as error:
            async with database.begin() as conn:
                await conn.execute(
                    insert(Booking.__table__).values(**booking(**second))
                )
        assert error.value.orig.sqlstate == "23P01"
        assert error.value.orig.__cause__.constraint_name == "bookings_no_overlap"


@pytest.mark.asyncio
async def test_cancelled_booking_does_not_block(database):
    async with database.begin() as conn:
        await conn.execute(insert(Booking.__table__).values(**booking()))
        await conn.execute(text("UPDATE bookings SET status='CANCELLED'"))
        await conn.execute(insert(Booking.__table__).values(**booking()))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "changes,constraint",
    [
        ({"guests": 0}, "ck_bookings_guests"),
        ({"check_out": date(2026, 10, 1)}, "ck_bookings_dates"),
    ],
)
async def test_database_checks(database, changes, constraint):
    with pytest.raises(IntegrityError) as error:
        async with database.begin() as conn:
            await conn.execute(insert(Booking.__table__).values(**booking(**changes)))
    assert error.value.orig.__cause__.constraint_name == constraint


@pytest.mark.asyncio
async def test_concurrent_requests_return_success_and_409(database):
    barrier = asyncio.Barrier(2)
    checked = []
    sessions = []
    factory = async_sessionmaker(database, expire_on_commit=False)

    class RacingRepository(BookingRepository):
        async def has_conflict(self, *args, **kwargs):
            conflict = await super().has_conflict(*args, **kwargs)
            checked.append(conflict)
            await asyncio.wait_for(barrier.wait(), timeout=10)
            return conflict

    async def session_override():
        async with factory() as session:
            sessions.append(session)
            yield session
            # The failed transaction must have been rolled back by the service.
            assert await session.scalar(select(1)) == 1

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[db_helper.session_getter] = session_override
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1, full_name="Test", username="test", email="test@example.com"
    )
    app.dependency_overrides[get_booking_service] = lambda: BookingService(
        RacingRepository()
    )
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            payload = {
                "room_id": 1,
                "check_in": "2026-10-01",
                "check_out": "2026-10-03",
                "guests": 1,
            }
            responses = await asyncio.wait_for(
                asyncio.gather(
                    client.post("/bookings", json=payload),
                    client.post("/bookings", json=payload),
                ),
                timeout=20,
            )
        assert sorted(r.status_code for r in responses) == [200, 409]
        assert (
            next(r for r in responses if r.status_code == 409).json()["error"]["code"]
            == "booking_conflict"
        )
        assert checked == [False, False]
        assert len(sessions) == 2 and sessions[0] is not sessions[1]
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(Booking)) == 1
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.asyncio
async def test_other_integrity_errors_are_not_booking_conflicts(database):
    from app.bookings.booking_schemas import BookingCreate

    factory = async_sessionmaker(database, expire_on_commit=False)
    async with factory() as session:
        # Nonexistent user triggers a foreign-key error during repository.flush().
        user = SimpleNamespace(id=99999, full_name="Test", email="test@example.com")
        data = BookingCreate(
            room_id=1, check_in="2026-10-01", check_out="2026-10-02", guests=1
        )
        with pytest.raises(IntegrityError) as error:
            await BookingService(BookingRepository()).create_booking(
                session, data, user
            )
        assert error.value.orig.sqlstate == "23503"
        assert await session.scalar(select(1)) == 1


@pytest.mark.asyncio
async def test_register_login_refresh_and_booking_ownership(database):
    factory = async_sessionmaker(database, expire_on_commit=False)

    async def session_override():
        async with factory() as session:
            yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[db_helper.session_getter] = session_override
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Fixture uses explicit ID 1; keep the PostgreSQL sequence in sync.
            async with database.begin() as conn:
                await conn.execute(
                    text("SELECT setval(pg_get_serial_sequence('users', 'id'), 1)")
                )
            registration = {
                "email": "new@example.com",
                "username": "newuser",
                "password": "Test-password-12345",
            }
            response = await client.post("/auth/register", json=registration)
            assert response.status_code == 201
            owner_id = response.json()["id"]
            assert "password_hash" not in response.json()
            assert (
                await client.post("/auth/register", json=registration)
            ).status_code == 409
            login = await client.post(
                "/auth/login",
                data={
                    "username": registration["email"],
                    "password": registration["password"],
                },
            )
            assert login.status_code == 200
            tokens = login.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            assert (await client.get("/auth/me", headers=headers)).json()[
                "id"
            ] == owner_id
            assert (
                await client.post(
                    "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
                )
            ).status_code == 200
            assert (
                await client.post(
                    "/auth/login",
                    data={
                        "username": registration["email"],
                        "password": "wrong-password",
                    },
                )
            ).status_code == 401
            # An unrelated user's booking must not appear in /users/me/bookings.
            async with database.begin() as conn:
                await conn.execute(
                    insert(Booking.__table__).values(**booking(room_id=2))
                )
            payload = {
                "room_id": 1,
                "check_in": "2026-10-01",
                "check_out": "2026-10-03",
                "guests": 1,
            }
            created = await client.post("/bookings", json=payload, headers=headers)
            assert created.status_code == 200
            own_booking = created.json()
            assert own_booking["total_price"] == 2000
            assert own_booking["user_id"] == owner_id
            own_list = await client.get("/users/me/bookings", headers=headers)
            assert own_list.status_code == 200
            assert [item["id"] for item in own_list.json()] == [own_booking["id"]]
            assert (
                await client.patch("/bookings/1/cancel", headers=headers)
            ).status_code == 404
            assert (
                await client.patch(
                    f"/bookings/{own_booking['id']}/cancel", headers=headers
                )
            ).status_code == 200
            assert (
                await client.post("/bookings", json=payload, headers=headers)
            ).status_code == 200
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
