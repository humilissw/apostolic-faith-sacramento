"""Tests for POST /api/v1/email/send."""

from __future__ import annotations

from unittest.mock import patch

from tests.conftest import make_token


def _sent_messages(mock) -> list[dict]:
    return [c.kwargs for c in mock.call_args_list]


class TestAuth:
    def test_missing_auth_is_401(self, client):
        r = client.post("/api/v1/email/send", json={"type": "test", "recipients": ["a@b.org"]})
        assert r.status_code == 401

    def test_invalid_token_is_401(self, client):
        r = client.post(
            "/api/v1/email/send",
            headers={"Authorization": "***"},
            json={"type": "test", "recipients": ["a@b.org"]},
        )
        assert r.status_code == 401

    def test_token_without_email_scope_is_403(self, client, no_scope_headers):
        r = client.post(
            "/api/v1/email/send",
            headers=no_scope_headers,
            json={"type": "test", "recipients": ["a@b.org"]},
        )
        assert r.status_code == 403
        assert "api:email" in r.json()["detail"]

    def test_superuser_token_always_allowed(self, client):
        headers = {"Authorization": f"Bearer {make_token(['superuser'])}"}
        with patch("app.api.routes.send.send_email") as m:
            r = client.post(
                "/api/v1/email/send",
                headers=headers,
                json={"type": "test", "recipients": ["a@b.org"]},
            )
        assert r.status_code == 200
        assert m.call_count == 1

    def test_bad_api_key_is_401(self, client):
        r = client.post(
            "/api/v1/email/send",
            headers={"X-API-Key": "wrong"},
            json={"type": "test", "recipients": ["a@b.org"]},
        )
        assert r.status_code == 401


class TestValidation:
    def test_password_reset_requires_token(self, client, auth_headers):
        r = client.post(
            "/api/v1/email/send",
            headers=auth_headers,
            json={"type": "password-reset", "recipients": ["a@b.org"]},
        )
        assert r.status_code == 422

    def test_announcement_requires_body(self, client, auth_headers):
        r = client.post("/api/v1/email/send", headers=auth_headers, json={"type": "announcement"})
        assert r.status_code == 422

    def test_unknown_type_rejected(self, client, auth_headers):
        r = client.post(
            "/api/v1/email/send",
            headers=auth_headers,
            json={"type": "spam", "recipients": ["a@b.org"]},
        )
        assert r.status_code == 422


class TestSend:
    def test_password_reset_embeds_backend_token(self, client, auth_headers):
        with patch("app.api.routes.send.send_email") as m:
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={
                    "type": "password-reset",
                    "recipients": ["user@afc.org"],
                    "token": "signed-token-abc.123",
                },
            )
        assert r.status_code == 200
        body = r.json()
        assert body["sent"] == 1 and body["failed"] == 0
        kwargs = _sent_messages(m)[0]
        assert kwargs["email_to"] == "user@afc.org"
        # The backend-generated token is embedded verbatim in the link.
        assert "signed-token-abc.123" in kwargs["html_content"]
        assert "reset-password?token=signed-token-abc.123" in kwargs["html_content"]

    def test_new_user_email(self, client, auth_headers):
        with patch("app.api.routes.send.send_email") as m:
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={
                    "type": "new-user",
                    "recipients": ["new@afc.org"],
                    "token": "welcome-token-xyz",
                    "valid_hours": 24,
                },
            )
        assert r.status_code == 200
        kwargs = _sent_messages(m)[0]
        assert "Set up your new account" in kwargs["subject"]
        assert "welcome-token-xyz" in kwargs["html_content"]

    def test_announcement_fans_out_to_all_users(self, client, auth_headers):
        with (
            patch(
                "app.api.routes.send.get_all_active_user_emails",
                return_value=["a@x.org", "b@y.org"],
            ),
            patch("app.api.routes.send.send_email") as m,
        ):
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={"type": "announcement", "body": "Prayer meeting Wednesday 7pm."},
            )
        assert r.status_code == 200
        body = r.json()
        assert body["sent"] == 2
        assert set(body["recipients"]) == {"a@x.org", "b@y.org"}
        assert m.call_count == 2
        assert "Prayer meeting Wednesday 7pm." in _sent_messages(m)[0]["html_content"]

    def test_announcement_targeted_skips_unknown_users(self, client, auth_headers):
        with (
            patch(
                "app.api.routes.send.filter_existing_users",
                return_value=(["known@x.org"], ["ghost@y.org"]),
            ),
            patch("app.api.routes.send.send_email") as m,
        ):
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={
                    "type": "announcement",
                    "body": "Hello",
                    "recipients": ["known@x.org", "ghost@y.org"],
                },
            )
        assert r.status_code == 200
        body = r.json()
        assert body["sent"] == 1
        assert body["recipients"] == ["known@x.org"]
        assert any(f["recipient"] == "ghost@y.org" for f in body["failures"])
        assert m.call_count == 1

    def test_per_recipient_failure_is_reported_not_raised(self, client, auth_headers):
        def flaky(**kwargs):
            if kwargs["email_to"] == "bad@x.org":
                raise RuntimeError("smtp down")

        with patch("app.api.routes.send.send_email", side_effect=flaky):
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={"type": "test", "recipients": ["good@x.org", "bad@x.org"]},
            )
        assert r.status_code == 200
        body = r.json()
        assert body["sent"] == 1 and body["failed"] == 1

    def test_api_key_server_to_server_send(self, client, api_key_headers):
        with patch("app.api.routes.send.send_email") as m:
            r = client.post(
                "/api/v1/email/send",
                headers=api_key_headers,
                json={"type": "password-reset", "recipients": ["forgot@afc.org"], "token": "t0k3n"},
            )
        assert r.status_code == 200
        assert m.call_count == 1

    def test_assignment_email(self, client, auth_headers):
        with patch("app.api.routes.send.send_email") as m:
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={
                    "type": "assignment",
                    "recipients": ["drums@afc.org"],
                    "assignment_type": "music",
                    "role": "worship team",
                    "event_date": "2026-09-20 10:00",
                    "instrument": "drums",
                },
            )
        assert r.status_code == 200
        kwargs = _sent_messages(m)[0]
        assert "Scheduler assignment" in kwargs["subject"]
        assert "drums" in kwargs["html_content"]


class TestTracking:
    def test_deliveries_are_recorded_in_service_db(self, client, auth_headers):
        from app.core.tracking import EmailDelivery, tracking_session_factory

        with patch("app.api.routes.send.send_email"):
            r = client.post(
                "/api/v1/email/send",
                headers=auth_headers,
                json={"type": "test", "recipients": ["track@x.org"]},
            )
        batch_id = r.json()["batch_id"]
        session = tracking_session_factory()()
        try:
            rows = session.query(EmailDelivery).filter_by(batch_id=batch_id).all()
            assert len(rows) == 1
            assert rows[0].status == "sent"
            assert rows[0].recipient == "track@x.org"
            assert rows[0].email_type == "test"
        finally:
            session.close()


class TestHealth:
    def test_health(self, client):
        r = client.get("/health/")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"
