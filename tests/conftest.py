import os

import pytest
from tank import Tank

# Set before importing app modules; unit tests never require a local .env file.
for key, value in {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_USER": "postgres",
    "DB_PASS": "postgres",
    "DB_NAME": "constraintbs_unit_unused",
    "JWT_SECRET_KEY": "test-only-signing-key-not-for-production-123456789",
}.items():
    os.environ.setdefault(key, value)


@pytest.fixture
def tank_factory():
    def _create_tank(analytics, hp=1000, shield=False):
        return Tank(hp=hp, shield=shield, analytics=analytics)

    return _create_tank
