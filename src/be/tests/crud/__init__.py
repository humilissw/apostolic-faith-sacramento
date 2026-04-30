import pytest

# Re-export for child test modules
from tests.conftest import db_session as _conftest_db_session  # noqa: F401


@pytest.fixture(name="db")
def db_alias(db_session_fixture):
    """Alias for db_session fixture."""
    return db_session_fixture
