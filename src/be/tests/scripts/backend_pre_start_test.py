from unittest.mock import AsyncMock, MagicMock, patch

from app.backend_pre_start import init, logger


async def test_init_successful_connection() -> None:
    session_mock = AsyncMock()
    execute_mock = AsyncMock(return_value=MagicMock())
    session_mock.configure_mock(**{"execute.return_value": execute_mock})

    with (
        patch("app.backend_pre_start.AsyncSessionLocal", return_value=session_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            await init(None)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."
