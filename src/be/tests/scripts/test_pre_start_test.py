from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.tests_pre_start import init, logger


def test_init_successful_connection() -> None:
    session_mock = MagicMock()
    exec_mock = MagicMock()
    scalar_mock = MagicMock()
    exec_mock.scalar_one_or_none.return_value = MagicMock()
    session_mock.exec.return_value = exec_mock
    session_mock.__enter__ = MagicMock(return_value=session_mock)
    session_mock.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.tests_pre_start.SyncSessionLocal", return_value=session_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(None)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert connection_successful, "The database connection should be successful and not raise an exception."

        assert session_mock.exec.call_count == 1, "The session should execute a select statement once."
