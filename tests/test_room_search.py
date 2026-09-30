from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.hotels.dependencies import get_room_service
from app.hotels.rooms.rooms_repository import RoomRepository
from app.main import app
from app.shared.database import db_helper


def test_search_amenities_are_query_parameters():
    operation = app.openapi()["paths"]["/rooms/search"]["get"]
    assert "requestBody" not in operation
    parameter = next(p for p in operation["parameters"] if p["name"] == "amenities")
    assert parameter["in"] == "query"


def test_search_passes_repeated_query_parameters_to_service():
    service = Mock(search_rooms=AsyncMock(return_value=[]))

    async def session_override():
        yield Mock()

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_room_service] = lambda: service
    app.dependency_overrides[db_helper.session_getter] = session_override
    try:
        with TestClient(app) as client:
            response = client.get(
                "/rooms/search?city=Krasnoyarsk&check_in=2026-09-30"
                "&check_out=2026-10-01&guests=1&amenities=1&amenities=2"
            )
        assert response.status_code == 200
        assert response.json() == []
        assert service.search_rooms.await_args.kwargs["amenities"] == [1, 2]
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.asyncio
async def test_search_builds_filter_for_each_amenity():
    session = AsyncMock()
    session.execute.return_value = Mock()
    session.execute.return_value.scalars.return_value.all.return_value = []
    await RoomRepository().search_rooms(
        session=session, city="Krasnoyarsk", check_in=date(2026, 9, 30),
        check_out=date(2026, 10, 1), guests=1, max_price=None,
        room_type=None, amenities=[1, 2],
    )
    statement = session.execute.await_args.args[0]
    sql = str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    assert "amenities.id = 1" in sql
    assert "amenities.id = 2" in sql
