"""
Configuration for repository tests.

This conftest provides fixtures for testing repository classes.
Prevents collection of parent conftest.py to avoid async fixture conflicts.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="function")
def mock_async_session():
    """
    Create a mock AsyncSession for testing repositories.
    This fixture returns a basic mock that can be configured by tests.
    """
    mock_session = MagicMock()

    # Mock the async methods
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.add = MagicMock()

    return mock_session


@pytest.fixture
def mock_execute_result():
    """Create a mock for session.execute() return value."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    return mock_result


@pytest.fixture
def mock_scalars():
    """Create a mock for scalars() method."""
    mock_scalars_result = MagicMock()
    mock_scalars_result.all.return_value = []
    return mock_scalars_result
