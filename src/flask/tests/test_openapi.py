"""Tests for OpenAPI spec generation."""


def test_openapi_spec_returns_valid_json(client):
    resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["openapi"] == "3.1.0"
    assert "paths" in data
    assert "components" in data
    assert "schemas" in data["components"]


def test_openapi_spec_has_required_paths(client):
    """Verify all known API paths appear in the spec."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    paths = data["paths"]

    # Core routes
    assert "/api/v1/login/pkce-challenge" in paths
    assert "/api/v1/login/access-token" in paths
    assert "/api/v1/login/refresh-token" in paths
    assert "/api/v1/login/logout" in paths
    assert "/api/v1/users" in paths
    assert "/api/v1/users/me" in paths
    assert "/api/v1/users/me/password" in paths
    assert "/api/v1/users/signup" in paths
    assert "/api/v1/users/admin/all" in paths
    assert "/api/v1/items" in paths
    assert "/api/v1/health" in paths
    assert "/api/v1/health/liveness" in paths
    assert "/api/v1/health/readiness" in paths
    assert "/api/v1/media" in paths
    assert "/api/v1/integrations" in paths
    assert "/api/v1/integrations/status" in paths
    assert "/api/v1/scheduler" in paths
    assert "/api/v1/scheduler/time-off-requests" in paths
    assert "/api/v1/payments" in paths
    assert "/api/v1/payments/config" in paths
    assert "/api/v1/admin/client-credentials" in paths
    assert "/api/v1/admin/client-credentials/{cc_id}" in paths
    assert "/api/v1/feature-flags" in paths
    assert "/api/v1/feature-flags/names" in paths
    assert "/api/v1/google/login/google" in paths
    assert "/api/v1/private/users/" in paths
    assert "/api/v1/video-uploads" in paths
    assert "/api/v1/password-recovery/{email}" in paths
    assert "/api/v1/reset-password/" in paths
    assert "/api/v1/utils/health-check/" in paths
    assert "/api/v1/utils/test-email/" in paths
    assert "/api/v1/church-services" in paths
    assert "/api/v1/members" in paths
    assert "/api/v1/announcements" in paths
    assert "/api/v1/feature-flags/pre-seed" in paths
    assert "/api/v1/users/admin/{user_id}/scopes" in paths


def test_openapi_spec_all_paths_have_tags(client):
    """Verify every path has tags assigned."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()

    for path, methods in data["paths"].items():
        for method, spec in methods.items():
            if path == "/":
                continue  # root is not an API endpoint
            if path == "/api/v1/" or path == "/api/v1":
                continue  # root API path has no specific tag
            assert "tags" in spec, f"Path {method.upper()} {path} missing tags"


def test_openapi_spec_all_paths_have_operation_id(client):
    """Verify every path has an operationId."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()

    for path, methods in data["paths"].items():
        for method, spec in methods.items():
            if path == "/":
                continue
            assert "operationId" in spec, f"Path {method.upper()} {path} missing operationId"


def test_openapi_spec_all_paths_have_responses(client):
    """Verify every path has response definitions."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()

    for path, methods in data["paths"].items():
        for method, spec in methods.items():
            assert "responses" in spec, f"Path {method.upper()} {path} missing responses"


def test_openapi_spec_schemas_included(client):
    """Verify key request/response schemas are in components/schemas."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    schemas = data["components"]["schemas"]

    # Key schemas from requests module
    assert "IntegrationCreate" in schemas
    assert "IntegrationUpdate" in schemas
    assert "TestConnectionRequest" in schemas
    assert "MediaCreate" in schemas
    assert "MediaUpdate" in schemas
    assert "VideoUploadCreate" in schemas
    assert "VideoUploadUpdate" in schemas
    assert "PaymentCreate" in schemas
    assert "FeatureFlagUpdateRequest" in schemas
    assert "BulkAssignRequest" in schemas
    assert "BulkAssignEntry" in schemas
    assert "TimeOffRequestCreate" in schemas
    assert "AssignmentCreate" in schemas
    assert "AssignmentUpdate" in schemas

    # Key schemas from responses module
    assert "IntegrationConfigPublic" in schemas
    assert "MediaPublic" in schemas
    assert "VideoUploadPublic" in schemas
    assert "PaymentPublic" in schemas
    assert "FeatureFlagPublic" in schemas
    assert "AssignmentPublic" in schemas
    assert "Token" in schemas  # from responses
    assert "UserPublic" in schemas  # from responses


def test_openapi_spec_httpvalidation_error_schema(client):
    """Verify HTTPValidationError schema exists."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    schemas = data["components"]["schemas"]
    assert "HTTPValidationError" in schemas


def test_openapi_spec_root_excluded(client):
    """Verify root HTML path is not in the API spec."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    assert "/" not in data["paths"], "Root path should not be in OpenAPI spec"


def test_openapi_spec_login_tagged(client):
    """Verify login endpoints are tagged 'login'."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    paths = data["paths"]

    login_path = paths.get("/api/v1/login/access-token", {})
    post_spec = login_path.get("post", {})
    assert "login" in post_spec.get("tags", []), "Login endpoints should be tagged 'login'"


def test_openapi_spec_integrations_tagged(client):
    """Verify integration endpoints are tagged 'integrations'."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    paths = data["paths"]

    int_path = paths.get("/api/v1/integrations", {})
    get_spec = int_path.get("get", {})
    assert "integrations" in get_spec.get("tags", []), "Integration endpoints should be tagged 'integrations'"


def test_openapi_spec_path_count(client):
    """Verify all expected paths are present."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    paths = data["paths"]

    # Filter out root
    api_paths = {p for p in paths if p != "/"}
    assert len(api_paths) >= 80, f"Expected at least 80 API paths, got {len(api_paths)}"


def test_openapi_spec_security_on_protected_endpoints(client):
    """Verify protected endpoints have security field."""
    resp = client.get("/api/v1/openapi.json")
    data = resp.get_json()
    paths = data["paths"]

    # Users list is protected
    users_get = paths.get("/api/v1/users", {}).get("get", {})
    assert "security" in users_get, "Users list should have security requirement"

    # Login access-token is public (auth endpoint)
    login_post = paths.get("/api/v1/login/access-token", {}).get("post", {})
    assert "security" not in login_post, "Login access-token should not require auth"
