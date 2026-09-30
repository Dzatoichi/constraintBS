import pytest
from tank import Tank

@pytest.fixture
def tank_factory():
    def _create_tank(analytics, hp=1000, shield=False):
        return Tank(hp=hp, shield=shield, analytics=analytics)
    
    return _create_tank