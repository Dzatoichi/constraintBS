from unittest.mock import Mock


def test_tank_is_destroyed_even_if_analytics_fails(tank_factory):
    analytics = Mock()
    analytics.send_event.side_effect = TimeoutError("analytics timeout")

    tank = tank_factory(
        analytics=analytics,
        hp=200,
    )

    tank.take_damage(200)

    assert tank.hp == 0
    assert tank.is_destroyed is True