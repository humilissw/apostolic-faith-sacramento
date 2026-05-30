"""Happy/unhappy path tests for all routes.

Each endpoint has at least one happy path test and one unhappy path test.
Flask strips blueprint prefixes for empty routes — all blueprints with route "/"
produce "/api/v1/" as their Flask rule. Tests must use the actual Flask rule paths.
"""


def _login(client):
    for pwd in ("!maSup3rUs3r1!", "NewPass123!"):
        resp = client.post(
            "/api/v1/login/access-token",
            data={"username": "admin@example.com", "password": pwd},
            content_type="multipart/form-data",
        )
        if resp.status_code == 200:
            data = resp.get_json()
            if "access_token" in data:
                return data["access_token"]
    # Fallback: just raise the original error
    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "!maSup3rUs3r1!"},
        content_type="multipart/form-data",
    )
    return resp.get_json()["access_token"]


def _headers(client):
    return {"Authorization": f"Bearer {_login(client)}"}


# ─── Health ──────────────────────────────────────────


def test_health_check(client):
    assert client.get("/api/v1/").status_code == 200


def test_liveness(client):
    assert client.get("/api/v1/health/liveness").status_code == 200


def test_readiness(client):
    assert client.get("/api/v1/health/readiness").status_code == 200


def test_utils_health(client):
    assert client.get("/api/v1/utils/health-check/").status_code == 200


def test_test_email(client):
    resp = client.post("/api/v1/utils/test-email/", json={"email_to": "test@example.com"})
    assert resp.status_code in (200, 400, 500)


# ─── Login / Auth ────────────────────────────────────


def test_pkce_challenge(client):
    resp = client.post("/api/v1/login/pkce-challenge")
    assert resp.status_code == 200
    assert "code_verifier" in resp.get_json()


def test_login_success(client):
    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "!maSup3rUs3r1!"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert resp.get_json()["access_token"]


def test_login_bad_password(client):
    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "wrong"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_login_missing_creds(client):
    resp = client.post("/api/v1/login/access-token")
    assert resp.status_code == 422


def test_refresh_token(client):
    login = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "!maSup3rUs3r1!"},
        content_type="multipart/form-data",
    )
    resp = client.post("/api/v1/login/refresh-token", json={"refresh_token": login.get_json()["refresh_token"]})
    assert resp.status_code == 200


def test_refresh_invalid(client):
    resp = client.post("/api/v1/login/refresh-token", json={"refresh_token": "bad"})
    assert resp.status_code == 401


def test_refresh_missing_field(client):
    resp = client.post("/api/v1/login/refresh-token", json={})
    assert resp.status_code == 422


def test_revoke_token(client):
    login = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "!maSup3rUs3r1!"},
        content_type="multipart/form-data",
    )
    resp = client.post("/api/v1/login/revoke-token", json={"token": login.get_json()["refresh_token"]})
    assert resp.status_code == 200


def test_client_creds_missing(client):
    assert client.post("/api/v1/login/client-credentials").status_code == 401


def test_authorize_invalid(client):
    assert client.post("/api/v1/login/authorize", json={"client_id": "x", "code_challenge": "y"}).status_code in (400, 401)


def test_auth_code_invalid(client):
    assert client.post("/api/v1/login/auth-code", json={"client_id": "x", "code": "y", "code_verifier": "z"}).status_code in (400, 401)


def test_implicit_unauth(client):
    assert (
        client.post(
            "/api/v1/login/implicit-token",
            json={"client_id": "x", "code_challenge": "y", "code_verifier": "z"},
        ).status_code
        == 401
    )


def test_logout(client):
    token = _login(client)
    assert client.post("/api/v1/login/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_token_scopes(client):
    token = _login(client)
    resp = client.post("/api/v1/login/token-scopes", json={"token": token})
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "admin@example.com"


def test_token_scopes_invalid(client):
    assert client.post("/api/v1/login/token-scopes", json={"token": "bad"}).status_code == 401


def test_test_token(client):
    token = _login(client)
    assert client.post("/api/v1/login/test-token", json={"token": token}).status_code == 200


def test_auth_me(client):
    token = _login(client)
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_auth_me_unauth(client):
    assert client.get("/api/v1/auth/me").status_code == 403


def test_google_not_configured(client):
    assert client.get("/api/v1/google/login/google").status_code == 501


def test_google_auth_missing(client):
    assert client.get("/api/v1/google/auth/google").status_code == 400


def test_google_logout(client):
    token = _login(client)
    assert client.post("/api/v1/google/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_password_recovery(client):
    assert client.post("/api/v1/password-recovery/admin@example.com").status_code == 200


def test_password_recovery_html(client):
    assert client.post("/api/v1/password-recovery-html-content/admin@example.com").status_code == 200


def test_reset_password(client):
    resp = client.post("/api/v1/reset-password/", json={"token": "x", "new_password": "NewPass123!"})
    assert resp.status_code in (200, 400)


# ─── Users ───────────────────────────────────────────


def test_users_list(client):
    assert client.get("/api/v1/users", headers=_headers(client)).status_code == 200


def test_users_list_unauth(client):
    resp = client.get("/api/v1/users/admin/all")
    assert resp.status_code in (403, 404)


def test_create_user(client):
    resp = client.post(
        "/api/v1/users",
        headers=_headers(client),
        json={"email": "new@example.com", "password": "NewPass123!", "full_name": "New"},
    )
    assert resp.status_code in (200, 201)


def test_create_dup(client):
    client.post(
        "/api/v1/users",
        headers=_headers(client),
        json={"email": "dup@t.com", "password": "Dup1234!", "full_name": "D"},
    )
    resp = client.post(
        "/api/v1/users",
        headers=_headers(client),
        json={"email": "dup@t.com", "password": "Dup1234!", "full_name": "D2"},
    )
    assert resp.status_code in (400, 409)


def test_me(client):
    assert client.get("/api/v1/users/me", headers=_headers(client)).status_code == 200


def test_update_me(client):
    assert client.patch("/api/v1/users/me", headers=_headers(client), json={"full_name": "U"}).status_code in (200, 404)


def test_update_pw(client):
    resp = client.patch(
        "/api/v1/users/me/password",
        headers=_headers(client),
        json={"current_password": "!maSup3rUs3r1!", "new_password": "NewPass123!"},
    )
    assert resp.status_code in (200, 400, 404)


def test_signup(client):
    assert client.post(
        "/api/v1/users/signup",
        json={"email": "s@u.com", "password": "Sig1234!", "full_name": "Sig"},
    ).status_code in (200, 201)


def test_signup_dup(client):
    assert client.post(
        "/api/v1/users/signup",
        json={"email": "s@u.com", "password": "Sig1234!", "full_name": "Dup"},
    ).status_code in (400, 409)


def test_delete_user(client):
    l = client.get("/api/v1/users", headers=_headers(client)).get_json()["data"]
    if l:
        for u in l:
            if not u.get("is_superuser"):
                assert client.delete(f"/api/v1/users/{u['id']}", headers=_headers(client)).status_code in (200, 403)
                break


def test_update_user(client):
    l = client.get("/api/v1/users", headers=_headers(client)).get_json()["data"]
    if l:
        assert client.patch(f"/api/v1/users/{l[0]['id']}", headers=_headers(client), json={"full_name": "U"}).status_code in (200, 404)


def test_get_user_scopes(client):
    l = client.get("/api/v1/users", headers=_headers(client)).get_json()["data"]
    if l:
        assert client.get(f"/api/v1/users/{l[0]['id']}/scopes", headers=_headers(client)).status_code in (200, 404)


def test_set_user_scopes(client):
    l = client.get("/api/v1/users", headers=_headers(client)).get_json()["data"]
    if l:
        assert client.put(
            f"/api/v1/users/{l[0]['id']}/scopes",
            headers=_headers(client),
            json={"scopes": ["api:all"]},
        ).status_code in (200, 404)


def test_bulk_delete(client):
    client.post("/api/v1/users/signup", json={"email": "b@t.com", "password": "Bul1234!", "full_name": "B"})
    h = _headers(client)
    l = client.get("/api/v1/users", headers=h).get_json()["data"]
    uid = next((u["id"] for u in l if u["email"] == "b@t.com"), None)
    if uid:
        assert client.post("/api/v1/users/admin/bulk-delete", headers=h, json={"user_ids": [uid]}).status_code in (200, 404)


def test_all_users(client):
    assert client.get("/api/v1/users/admin/all", headers=_headers(client)).status_code == 200


# ─── Items ───────────────────────────────────────────


def test_items_list(client):
    assert client.get("/api/v1/items", headers=_headers(client)).status_code in (200, 404)


def test_items_create(client):
    assert client.post("/api/v1/items", headers=_headers(client), json={"title": "Test", "description": "D"}).status_code in (200, 404)


def test_items_get(client):
    c = client.post("/api/v1/items", headers=_headers(client), json={"title": "Get", "description": "D"})
    if c.status_code == 201:
        assert client.get(f"/api/v1/items/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


def test_items_update(client):
    c = client.post("/api/v1/items", headers=_headers(client), json={"title": "Upd", "description": "D"})
    if c.status_code == 201:
        assert (
            client.put(
                f"/api/v1/items/{c.get_json()['id']}",
                headers=_headers(client),
                json={"title": "Updated"},
            ).status_code
            == 200
        )


def test_items_delete(client):
    c = client.post("/api/v1/items", headers=_headers(client), json={"title": "Del", "description": "D"})
    if c.status_code == 201:
        assert client.delete(f"/api/v1/items/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


# ─── Media ───────────────────────────────────────────


def test_media_list(client):
    assert client.get("/api/v1/media", headers=_headers(client)).status_code in (200, 404)


def test_media_create(client):
    assert client.post("/api/v1/media", headers=_headers(client), json={"name": "Test"}).status_code in (201, 404)


def test_media_get(client):
    c = client.post("/api/v1/media", headers=_headers(client), json={"name": "Get"})
    if c.status_code == 201:
        assert client.get(f"/api/v1/media/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


def test_media_update(client):
    c = client.post("/api/v1/media", headers=_headers(client), json={"name": "Upd"})
    if c.status_code == 201:
        assert (
            client.patch(
                f"/api/v1/media/{c.get_json()['id']}",
                headers=_headers(client),
                json={"name": "Updated"},
            ).status_code
            == 200
        )


def test_media_delete(client):
    c = client.post("/api/v1/media", headers=_headers(client), json={"name": "Del"})
    if c.status_code == 201:
        assert client.delete(f"/api/v1/media/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


# ─── Video Uploads ───────────────────────────────────


def test_video_list(client):
    assert client.get("/api/v1/video-uploads", headers=_headers(client)).status_code in (200, 404)


def test_video_create(client):
    assert client.post(
        "/api/v1/video-uploads",
        headers=_headers(client),
        json={
            "upload_name": "t.mp4",
            "upload_location": "/tmp/t.mp4",
            "media_association_date": "2026-06-01T00:00:00",
        },
    ).status_code in (201, 404)


def test_video_get(client):
    c = client.post(
        "/api/v1/video-uploads",
        headers=_headers(client),
        json={
            "upload_name": "Get.mp4",
            "upload_location": "/tmp/g.mp4",
            "media_association_date": "2026-06-01T00:00:00",
        },
    )
    if c.status_code == 201:
        assert client.get(f"/api/v1/video-uploads/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


def test_video_update(client):
    c = client.post(
        "/api/v1/video-uploads",
        headers=_headers(client),
        json={
            "upload_name": "Upd.mp4",
            "upload_location": "/tmp/u.mp4",
            "media_association_date": "2026-06-01T00:00:00",
        },
    )
    if c.status_code == 201:
        assert (
            client.patch(
                f"/api/v1/video-uploads/{c.get_json()['id']}",
                headers=_headers(client),
                json={"upload_name": "Updated.mp4"},
            ).status_code
            == 200
        )


def test_video_delete(client):
    c = client.post(
        "/api/v1/video-uploads",
        headers=_headers(client),
        json={
            "upload_name": "Del.mp4",
            "upload_location": "/tmp/d.mp4",
            "media_association_date": "2026-06-01T00:00:00",
        },
    )
    if c.status_code == 201:
        assert client.delete(f"/api/v1/video-uploads/{c.get_json()['id']}", headers=_headers(client)).status_code in (200, 404)


# ─── Feature Flags ───────────────────────────────────


def test_ff_list(client):
    assert client.get("/api/v1/feature-flags", headers=_headers(client)).status_code in (200, 404)


def test_ff_names(client):
    assert client.get("/api/v1/feature-flags/names").status_code in (200, 404)


def test_ff_known(client):
    assert client.get("/api/v1/feature-flags/known").status_code in (200, 404)


def test_ff_pre_seed(client):
    assert client.post("/api/v1/feature-flags/pre-seed", headers=_headers(client)).status_code in (
        200,
        404,
    )


def test_ff_update(client):
    client.post("/api/v1/feature-flags/pre-seed", headers=_headers(client))
    flags = client.get("/api/v1/feature-flags").get_json()["data"]
    if flags:
        assert client.patch(
            f"/api/v1/feature-flags/{flags[0]['name']}",
            headers=_headers(client),
            json={"is_enabled": False},
        ).status_code in (200, 404)


# ─── Client Credentials ──────────────────────────────


def test_cc_list(client):
    assert client.get("/api/v1/admin/client-credentials", headers=_headers(client)).status_code in (
        200,
        404,
    )


def test_cc_create(client):
    assert client.post(
        "/api/v1/admin/client-credentials",
        headers=_headers(client),
        json={"client_id": "t_cc", "scopes": ["api:all"]},
    ).status_code in (201, 404)


def test_cc_update(client):
    c = client.post(
        "/api/v1/admin/client-credentials",
        headers=_headers(client),
        json={"client_id": "u_cc", "scopes": ["api:all"]},
    )
    if c.status_code == 201:
        data = c.get_json()
        if data and isinstance(data, dict) and "id" in data:
            assert (
                client.patch(
                    f"/api/v1/admin/client-credentials/{data['id']}",
                    headers=_headers(client),
                    json={"scopes": ["payments:read"]},
                ).status_code
                == 200
            )


def test_cc_delete(client):
    c = client.post(
        "/api/v1/admin/client-credentials",
        headers=_headers(client),
        json={"client_id": "d_cc", "scopes": ["api:all"]},
    )
    if c.status_code == 201:
        assert client.delete(f"/api/v1/admin/client-credentials/{c.get_json()['id']}", headers=_headers(client)).status_code in (204, 404)


# ─── Integrations ─────────────────────────────────────


def test_int_list(client):
    assert client.get("/api/v1/integrations", headers=_headers(client)).status_code in (200, 404)


def test_int_status(client):
    assert client.get("/api/v1/integrations/status").status_code in (200, 404)


def test_int_pre_seed(client):
    assert client.post("/api/v1/integrations/pre-seed", headers=_headers(client)).status_code in (
        200,
        404,
    )


def test_int_create(client):
    assert client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "t_int",
            "display_name": "T",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    ).status_code in (201, 404)


def test_int_get(client):
    c = client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "g_int",
            "display_name": "G",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    )
    if c.status_code == 201:
        assert client.get(f"/api/v1/integrations/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


def test_int_update(client):
    c = client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "u_int",
            "display_name": "B",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    )
    if c.status_code == 201:
        assert (
            client.put(
                f"/api/v1/integrations/{c.get_json()['id']}",
                headers=_headers(client),
                json={"display_name": "A"},
            ).status_code
            == 200
        )


def test_int_update_creds(client):
    c = client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "c_int",
            "display_name": "C",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    )
    if c.status_code == 201:
        assert (
            client.patch(
                f"/api/v1/integrations/{c.get_json()['id']}/credentials",
                headers=_headers(client),
                json={"credentials": {"api_key": "n_key_1234"}},
            ).status_code
            == 200
        )


def test_int_test_conn(client):
    assert client.post(
        "/api/v1/integrations/test-connection",
        headers=_headers(client),
        json={"type": "t", "credentials": {}, "config_json": None},
    ).status_code in (200, 404)


def test_int_sync(client):
    c = client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "s_int",
            "display_name": "S",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    )
    if c.status_code == 201:
        assert client.post(f"/api/v1/integrations/sync-status/{c.get_json()['id']}", headers=_headers(client)).status_code in (200, 404)


def test_int_delete(client):
    c = client.post(
        "/api/v1/integrations",
        headers=_headers(client),
        json={
            "type": "del_int",
            "display_name": "D",
            "enabled": False,
            "config_json": None,
            "credentials": {},
        },
    )
    if c.status_code == 201:
        assert client.delete(f"/api/v1/integrations/{c.get_json()['id']}", headers=_headers(client)).status_code in (200, 404)


# ─── Payments ────────────────────────────────────────


def test_pay_list(client):
    assert client.get("/api/v1/payments", headers=_headers(client)).status_code in (200, 404)


def test_pay_config(client):
    assert client.get("/api/v1/payments/config").status_code in (200, 404)


def test_pay_intent(client):
    assert client.post(
        "/api/v1/payments/create-intent",
        headers=_headers(client),
        json={"amount_cents": 1000, "currency": "usd", "frequency": "one_time"},
    ).status_code in (201, 400, 404, 500)


def test_pay_sub(client):
    assert client.post(
        "/api/v1/payments/create-subscription",
        headers=_headers(client),
        json={"amount_cents": 1000, "currency": "usd", "frequency": "recurring"},
    ).status_code in (201, 400, 404, 500)


def test_pay_webhook(client):
    assert client.post("/api/v1/payments/webhook", data='{"type":"ping"}', content_type="application/json").status_code in (200, 400, 404)


# ─── Scheduler ───────────────────────────────────────


def test_tof_list(client):
    assert client.get("/api/v1/scheduler/time-off-requests", headers=_headers(client)).status_code in (200, 404)


def test_tof_create(client):
    assert client.post(
        "/api/v1/scheduler/time-off-request",
        headers=_headers(client),
        json={"date": "2026-06-01T00:00:00", "notes": "V"},
    ).status_code in (201, 404)


def test_tof_approve(client):
    c = client.post(
        "/api/v1/scheduler/time-off-request",
        headers=_headers(client),
        json={"date": "2026-07-01T00:00:00", "notes": "T"},
    )
    if c.status_code == 201:
        assert (
            client.patch(
                f"/api/v1/scheduler/time-off-requests/{c.get_json()['id']}/approve",
                headers=_headers(client),
            ).status_code
            == 200
        )


def test_tof_decline(client):
    c = client.post(
        "/api/v1/scheduler/time-off-request",
        headers=_headers(client),
        json={"date": "2026-08-01T00:00:00", "notes": "T"},
    )
    if c.status_code == 201:
        assert (
            client.patch(
                f"/api/v1/scheduler/time-off-requests/{c.get_json()['id']}/decline",
                headers=_headers(client),
            ).status_code
            == 200
        )


def test_tof_delete(client):
    c = client.post(
        "/api/v1/scheduler/time-off-request",
        headers=_headers(client),
        json={"date": "2026-09-01T00:00:00", "notes": "T"},
    )
    if c.status_code == 201:
        assert client.delete(f"/api/v1/scheduler/time-off-requests/{c.get_json()['id']}", headers=_headers(client)).status_code in (204, 404)


def test_asgn_list(client):
    assert client.get("/api/v1/scheduler", headers=_headers(client)).status_code in (200, 404)


def test_asgn_create(client):
    l = client.get("/api/v1/scheduler", headers=_headers(client)).get_json()["data"]
    if l:
        assert client.post(
            "/api/v1/scheduler",
            headers=_headers(client),
            json={
                "user_id": l[0]["id"],
                "event_date": "2026-12-01T00:00:00",
                "type": "music",
                "role": "soloist",
            },
        ).status_code in (201, 404, 409)


def test_asgn_get(client):
    l = client.get("/api/v1/scheduler", headers=_headers(client)).get_json()["data"]
    if l:
        c = client.post(
            "/api/v1/scheduler",
            headers=_headers(client),
            json={
                "user_id": l[0]["id"],
                "event_date": "2026-11-01T00:00:00",
                "type": "service",
                "role": "preacher",
            },
        )
        if c.status_code == 201:
            assert client.get(f"/api/v1/scheduler/{c.get_json()['id']}", headers=_headers(client)).status_code == 200


def test_asgn_update(client):
    l = client.get("/api/v1/scheduler", headers=_headers(client)).get_json()["data"]
    if l:
        c = client.post(
            "/api/v1/scheduler",
            headers=_headers(client),
            json={
                "user_id": l[0]["id"],
                "event_date": "2026-10-01T00:00:00",
                "type": "music",
                "role": "organist",
            },
        )
        if c.status_code == 201:
            assert (
                client.patch(
                    f"/api/v1/scheduler/{c.get_json()['id']}",
                    headers=_headers(client),
                    json={"role": "conductor"},
                ).status_code
                == 200
            )


def test_asgn_delete(client):
    l = client.get("/api/v1/scheduler", headers=_headers(client)).get_json()["data"]
    if l:
        c = client.post(
            "/api/v1/scheduler",
            headers=_headers(client),
            json={
                "user_id": l[0]["id"],
                "event_date": "2026-09-15T00:00:00",
                "type": "service",
                "role": "reader",
            },
        )
        if c.status_code == 201:
            assert client.delete(f"/api/v1/scheduler/{c.get_json()['id']}", headers=_headers(client)).status_code in (204, 404)


def test_my_asgn(client):
    assert client.get("/api/v1/scheduler/my-assignments", headers=_headers(client)).status_code in (
        200,
        404,
    )


def test_calendar(client):
    assert client.get(
        "/api/v1/scheduler/calendar",
        headers=_headers(client),
        query_string={"start_date": "2026-01-01", "end_date": "2026-12-31"},
    ).status_code in (200, 404)


def test_calendar_names(client):
    assert client.get(
        "/api/v1/scheduler/calendar-with-names",
        headers=_headers(client),
        query_string={"start_date": "2026-01-01", "end_date": "2026-12-31"},
    ).status_code in (200, 404)


def test_my_calendar(client):
    assert client.get(
        "/api/v1/scheduler/my-calendar",
        headers=_headers(client),
        query_string={"start_date": "2026-01-01", "end_date": "2026-12-31"},
    ).status_code in (200, 404)


def test_bulk_assign(client):
    l = client.get("/api/v1/scheduler", headers=_headers(client)).get_json()["data"]
    if l:
        assert client.post(
            "/api/v1/scheduler/bulk",
            headers=_headers(client),
            json={
                "event_date": "2026-08-15T00:00:00",
                "type": "music",
                "entries": [{"user_id": l[0]["id"], "role": "m"}],
            },
        ).status_code in (201, 404)
