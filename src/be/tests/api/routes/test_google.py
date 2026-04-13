import pytest
from fastapi import Request
from unittest.mock import Mock, patch


def test_google_login_route(client) -> None:
    """Test Google login redirect endpoint."""
    with patch("app.api.routes.google.oauth") as mock_oauth:
        mock_request = Mock(spec=Request)
        mock_request.url_for = Mock(return_value="https://example.com/callback")

        mock_authorize_redirect = Mock()
        mock_oauth.google.authorize_redirect = mock_authorize_redirect

        response = client.get("/api/v1/google/login")
        assert response.status_code == 200
        mock_oauth.google.authorize_redirect.assert_called_once()


def test_google_auth_route(client) -> None:
    """Test Google authorization endpoint."""
    with patch("app.api.routes.google.oauth") as mock_oauth:
        mock_request = Mock(spec=Request)

        mock_token = {"userinfo": {"email": "test@example.com", "name": "Test User"}}
        mock_oauth.google.authorize_access_token = Mock(return_value=mock_token)

        response = client.get("/api/v1/google/auth")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
        assert response.json()["name"] == "Test User"