"""OpenAPI 3.1 spec generation and Swagger UI for the AFC API.

Serves:
  /docs            — Swagger UI
  /openapi.json    — OpenAPI 3.1 spec (also at /api/v1/openapi.json)
"""

from ast import AST, parse, unparse
from inspect import getsource
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, current_app
from pydantic import BaseModel
from pydantic.type_adapter import TypeAdapter

openapi_bp = Blueprint("openapi", __name__)

# ─── Tag map: full Flask path prefix → tag name (longest-first) ───

_TAG_MAP = [
    ("/api/v1/scheduler/", "scheduler"),
    ("/api/v1/integrations/", "integrations"),
    ("/api/v1/payments/", "payments"),
    ("/api/v1/users/admin/", "user-scopes"),
    ("/api/v1/users/", "users"),
    ("/api/v1/google/", "authentication"),
    ("/api/v1/login/", "login"),
    ("/api/v1/auth/", "login"),
    ("/api/v1/password-recovery/", "login"),
    ("/api/v1/reset-password", "login"),
    ("/api/v1/password-recovery-html-content", "login"),
    ("/api/v1/admin/", "client-credentials"),
    ("/api/v1/feature-flags/", "feature-flags"),
    ("/api/v1/video-uploads/", "video-uploads"),
    ("/api/v1/media/", "media"),
    ("/api/v1/health/", "health"),
    ("/api/v1/church-services/", "church-services"),
    ("/api/v1/announcements/", "announcements"),
    ("/api/v1/members/", "members"),
    ("/api/v1/utils/", "utils"),
    ("/api/v1/items/", "items"),
    ("/api/v1/private/", "private"),
]


# ─── Helpers ────────────────────────────────────────────────────────────


def _parse_params(rule) -> list[dict]:
    """Extract path parameters from a Flask rule."""
    params: list[dict] = []
    for segment in rule.rule.split("/"):
        if "<" in segment and ">" in segment:
            param_name = segment.strip("<>").split(":", 1)[-1]
            params.append(
                {
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            )
    return params


def _find_pydantic_model(ret_val: str) -> tuple[str, dict | None]:
    """Find a Pydantic model referenced in a return expression."""
    for module_name in [
        "backend.models",
        "backend.responses",
        "backend.requests",
    ]:
        try:
            mod = __import__(module_name, fromlist=[""])
            for attr_name in dir(mod):
                obj = getattr(mod, attr_name)
                if isinstance(obj, type) and issubclass(obj, BaseModel):
                    schema = TypeAdapter(obj).json_schema()
                    if attr_name in ret_val or f".{attr_name}(" in ret_val:
                        return attr_name, schema
        except Exception:
            continue
    return "", None


def _collect_all_schemas() -> dict[str, dict]:
    """Collect ALL Pydantic schemas from requests, responses, and models modules."""
    schemas: dict[str, dict] = {}

    # Scan every Python file in requests/ and responses/ subpackages
    base = Path(__file__).parent
    for pkg in ["requests", "responses"]:
        pkg_dir = base / pkg
        if not pkg_dir.is_dir():
            continue
        for pyfile in pkg_dir.glob("*.py"):
            if pyfile.name.startswith("__"):
                continue
            mod_name = f"backend.{pkg}.{pyfile.stem}"
            try:
                mod = __import__(mod_name, fromlist=[""])
                for attr_name in dir(mod):
                    obj = getattr(mod, attr_name)
                    if isinstance(obj, type) and issubclass(obj, BaseModel):
                        schemas[attr_name] = TypeAdapter(obj).json_schema()
            except Exception:
                continue

    # Also scan backend.models (DB models)
    try:
        mod = __import__("backend.models", fromlist=[""])
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if isinstance(obj, type) and issubclass(obj, BaseModel):
                # Only include if not already from requests/responses
                if attr_name not in schemas:
                    schemas[attr_name] = TypeAdapter(obj).json_schema()
    except Exception:
        pass

    return schemas


def _get_response_codes(func) -> list[int]:
    """Extract HTTP status codes from route function return statements."""
    codes: list[int] = []
    try:
        source = getsource(func)
        tree = parse(source)
    except Exception:
        return []

    for node in tree.walk(tree):
        if not isinstance(node, AST.Return) or node.value is None:
            continue
        ret = unparse(node.value).strip()
        # Tuple return: jsonify(...), code
        if isinstance(node.value, AST.Tuple):
            elts = node.value.elts
            if len(elts) >= 2:
                second = elts[1]
                if isinstance(second, AST.Constant) and isinstance(second.value, int):
                    codes.append(second.value)
                elif isinstance(second, AST.Name):
                    # Skip variable names — can't resolve statically
                    pass
        # Single jsonify/JSON response → default 200
        if "jsonify" in ret or "model_dump" in ret or "json(" in ret:
            if 200 not in codes:
                codes.insert(0, 200)
        # Redirect returns
        if "redirect" in ret.lower():
            if 302 not in codes:
                codes.append(302)

    return codes


def _get_request_content_type(func) -> str:
    """Detect request content type from route function source."""
    try:
        source = getsource(func)
        if "form_urlencoded" in source or "application/x-www-form-urlencoded" in source:
            return "application/x-www-form-urlencoded"
        if "multipart" in source:
            return "multipart/form-data"
        if "get_json" in source or "request.json" in source:
            return "application/json"
    except Exception:
        pass
    return "application/json"


def _get_request_body_schema(func, schemas: dict[str, dict]) -> dict | None:
    """Build requestBody schema for POST/PUT/PATCH endpoints."""
    content_type = _get_request_content_type(func)
    try:
        source = getsource(func)
        tree = parse(source)
    except Exception:
        return None

    # Look for Pydantic model usage in request parsing
    for node in tree.walk(tree):
        if isinstance(node, AST.Call):
            call_str = unparse(node).strip() if hasattr(node, "value") else ""
            # Check for model instantiation from request data
            for elt in getattr(node, "args", []):
                try:
                    val_str = unparse(elt).strip()
                    for schema_name in schemas:
                        if schema_name in val_str:
                            return {
                                "content": {content_type: {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}},
                                "required": True,
                            }
                except Exception:
                    continue

    # Fallback: detect form data for login routes
    try:
        source = getsource(func)
        if "form_data" in source or "Request" in source:
            # Generate a generic form schema
            return {
                "content": {
                    content_type: {
                        "schema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                        }
                    }
                },
                "required": True,
            }
    except Exception:
        pass

    # Generic JSON body
    if content_type == "application/json":
        return {
            "content": {"application/json": {"schema": {"type": "object", "properties": {}, "required": []}}},
            "required": True,
        }

    return None


def _get_all_response_descriptions(func) -> list[dict]:
    """Build response descriptions from a route function's return statements."""
    codes = _get_response_codes(func)
    if not codes:
        codes = [200]

    try:
        source = getsource(func)
        tree = parse(source)
    except Exception:
        return {str(c): {"description": "Success"} for c in codes}

    responses: dict[str, dict] = {}
    code_idx = 0

    for node in tree.walk(tree):
        if not isinstance(node, AST.Return) or node.value is None:
            continue
        ret_val = unparse(node.value).strip()
        has_json = "jsonify" in ret_val or "model_dump" in ret_val or "json(" in ret_val
        if not has_json:
            continue

        model_name, schema = _find_pydantic_model(ret_val)
        resp: dict[str, Any] = {"description": "Success"}
        if schema:
            resp["content"] = {"application/json": {"schema": schema, "example": {}}}
        code = codes[code_idx] if code_idx < len(codes) else 200
        responses[str(code)] = resp
        code_idx += 1

    # Fill in missing codes
    for code in codes:
        if str(code) not in responses:
            responses[str(code)] = {"description": "Success"}

    return responses


def _build_spec():
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "AFC API",
            "version": "0.1.0",
            "description": "Apostolic Faith Sacramento API",
        },
        "servers": [],
        "paths": {},
        "components": {"schemas": {}},
    }

    # Collect ALL Pydantic schemas
    spec["components"]["schemas"] = _collect_all_schemas()

    # Add HTTPValidationError schema
    if "HTTPValidationError" not in spec["components"]["schemas"]:
        spec["components"]["schemas"]["HTTPValidationError"] = {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ValidationError"},
                }
            },
        }
    if "ValidationError" not in spec["components"]["schemas"]:
        spec["components"]["schemas"]["ValidationError"] = {
            "type": "object",
            "required": ["loc", "msg", "type"],
            "properties": {
                "loc": {"type": "array", "items": {"type": "string"}},
                "msg": {"type": "string"},
                "type": {"type": "string"},
            },
        }

    app = current_app
    if app is None:
        return spec

    for rule in app.url_map.iter_rules():
        allowed = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        methods = [m for m in rule.methods if m in allowed]
        if not methods:
            continue

        if rule.endpoint and (rule.endpoint.startswith("static") or rule.endpoint.startswith("openapi.")):
            continue

        # Skip the openapi.json endpoint itself (it's the spec, not an API route)
        if rule.rule in ("/openapi.json", "/api/v1/openapi.json"):
            continue

        # Skip root path (HTML page, not an API endpoint)
        if rule.rule == "/":
            continue

        # Reconstruct the full OpenAPI path from the endpoint name
        # Flask's rule.rule strips blueprint prefix for empty routes, so we reconstruct
        endpoint = rule.endpoint or ""
        endpoint_parts = endpoint.split(".")
        blueprint_name = endpoint_parts[0] if endpoint_parts else ""

        # Blueprint → URL prefix mapping (for routes that lose their prefix)
        _BLUEPRINT_PREFIXES = {
            "users": "/api/v1/users",
            "utils": "/api/v1/utils",
            "items": "/api/v1/items",
            "health": "/api/v1/health",
            "church_services": "/api/v1/church-services",
            "media": "/api/v1/media",
            "members": "/api/v1/members",
            "video_uploads": "/api/v1/video-uploads",
            "announcements": "/api/v1/announcements",
            "google": "/api/v1/google",
            "payments": "/api/v1/payments",
            "scheduler": "/api/v1/scheduler",
            "feature_flags": "/api/v1/feature-flags",
            "client_credentials": "/api/v1/admin",
            "user_scopes": "/api/v1/users/admin",
            "integrations": "/api/v1/integrations",
            "private": "/api/v1/private",
        }

        bp_prefix = _BLUEPRINT_PREFIXES.get(blueprint_name, "/api/v1")

        # Reconstruct the full OpenAPI path
        if blueprint_name in _BLUEPRINT_PREFIXES and rule.rule.startswith("/api/v1"):
            # Check if rule.rule already contains the blueprint prefix
            # Flask preserves it for some routes but strips it for empty routes
            if rule.rule.startswith(bp_prefix + "/") or rule.rule == bp_prefix.rstrip("/"):
                # Blueprint prefix present in rule.rule — use as-is
                full_path = rule.rule
            else:
                # Blueprint prefix missing (Flask strips for empty routes) — reconstruct
                suffix = rule.rule[len("/api/v1") :] or "/"
                full_path = bp_prefix.rstrip("/") + suffix
        else:
            full_path = rule.rule

        # Convert Flask path params <type:name> -> {name}
        # Preserve trailing slash for path identity (e.g. /api/v1/users/ vs /api/v1/users)
        segments = full_path.split("/")
        path_parts = []
        for segment in segments:
            if segment:
                if "<" in segment:
                    param_name = segment.strip("<>").split(":", 1)[-1]
                    path_parts.append("{" + param_name + "}")
                else:
                    path_parts.append(segment)
        path = "/" + "/".join(path_parts)
        if full_path.endswith("/") and not path.endswith("/"):
            path += "/"

        # Find tag by matching against the full reconstructed path
        tag = None
        for prefix, group_tag in _TAG_MAP:
            if path.startswith(prefix) or path.rstrip("/").startswith(prefix.rstrip("/")):
                tag = group_tag
                break

        for method in methods:
            handler_name = rule.endpoint.split(".")[-1] if rule.endpoint else "unknown"

            # Generate operationId: "{func_name}_{path_snake}_{method}"
            path_snake = path.replace("/", "_").strip("_")
            operation_id = f"{handler_name}_{path_snake}_{method.lower()}"

            view_func = app.view_functions.get(handler_name) if handler_name != "unknown" else None
            try:
                resps = _get_all_response_descriptions(view_func) if view_func else {}
            except Exception:
                resps = {}

            entry: dict[str, Any] = {
                "summary": handler_name.replace("_", " ").title(),
                "operationId": operation_id,
                "parameters": _parse_params(rule),
                "responses": resps if resps else {"200": {"description": "Success"}},
            }

            if tag:
                entry["tags"] = [tag]

            # Add requestBody for POST/PUT/PATCH
            if method in ("POST", "PUT", "PATCH"):
                rb = _get_request_body_schema(view_func, spec["components"]["schemas"]) if view_func else None
                if rb:
                    entry["requestBody"] = rb

            # Add security for non-public endpoints
            if tag not in ("login",):
                entry["security"] = [{"bearerAuth": []}]

            spec["paths"].setdefault(path, {})
            spec["paths"][path][method.lower()] = entry

    return spec


# ─── Routes ───────────────────────────────────────────────────────────────


@openapi_bp.route("/openapi.json")
def get_openapi_spec():
    spec = _build_spec()
    return jsonify(spec)


SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AFC API Docs</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
<style>html{box-sizing:border-box}*{margin:0;padding:0}body{margin:24px;max-width:1440px}</style>
</head>
<body><div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
        crossorigin="anonymous"></script>
<script>
window.onload = () => {
  const specUrl = '/openapi.json';
  window.ui = SwaggerUIBundle({
    url: specUrl,
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [SwaggerUIBundle.presets.apis],
    syntaxHighlight: { activate: true },
    defaultModelsExpandDepth: 2,
    docExpansion: 'list',
  });
};
</script>
</body>
</html>"""


@openapi_bp.route("/docs")
def swagger_docs():
    return SWAGGER_HTML
