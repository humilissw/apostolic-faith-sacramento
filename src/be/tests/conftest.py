from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, text

from app.config import settings
from app.core.db import engine, async_engine, init_db_async
from app.main import app
from app.models import Item, User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """Session-scoped database fixture for all tests."""
    with Session(engine) as session:
        init_db_async(async_engine)
        yield session
        # Clean up after all tests
        try:
            statement = delete(Item)
            session.execute(statement)
            statement = delete(User)
            session.execute(statement)
            session.commit()
        except Exception:
            session.rollback()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Module-scoped test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Superuser authentication headers."""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Normal user authentication headers."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
def db_session(db: Session) -> Session:
    """Function-scoped database session for individual tests."""
    # Create a fresh session for each test
    test_session = Session(engine)
    try:
        yield test_session
    finally:
        # Clean up after each test
        try:
            statement = delete(Item)
            test_session.execute(statement)
            statement = delete(User)
            test_session.execute(statement)
            test_session.commit()
        except Exception:
            test_session.rollback()
        finally:
            test_session.close()