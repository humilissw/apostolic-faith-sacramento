import pytest

# Import the parent conftest fixtures
from tests.conftest import db_session


@pytest.fixture(name="db")
def db_alias(db_session):
    """Alias for db_session fixture."""
    return db_session
