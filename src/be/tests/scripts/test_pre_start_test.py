from unittest.mock import MagicMock, patch


from app.tests_pre_start import init, logger


def test_init_successful_connection() -> None:
    result_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.execute.return_value = result_mock
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

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        assert (
            session_mock.execute.call_count == 1
        ), "The session should execute a select statement once."
