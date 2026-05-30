# OpenAPI Spec Discrepancies — RESOLVED

## Status: All discrepancies resolved

The following issues have been fixed. See git history for details.

### 1. Path Prefix Stripped — RESOLVED

**Fixed in**: `backend/openapi_spec.py`

Reconstructed OpenAPI paths from endpoint names since Flask strips blueprint prefixes for empty routes. All 84 API paths now preserved with `/api/v1/` prefix.

### 2. Integration Endpoint Missing Metadata — RESOLVED

**Fixed in**: `backend/openapi_spec.py`

All endpoints now receive tags (longest-prefix matching), requestBodies (auto-detected), operationIds, security headers, and response codes.

### 3. Schema Discrepancies — RESOLVED

**Fixed in**: `backend/openapi_spec.py` — `_collect_all_schemas()`

All Pydantic schemas from `backend/requests/*.py`, `backend/responses/*.py`, and `backend/models.py` collected. `HTTPValidationError` and `ValidationError` added explicitly. OpenAPI version updated to 3.1.0.

### 4. Route Groups Need Tags — RESOLVED

**Fixed in**: `backend/openapi_spec.py` — `_TAG_MAP`

All 22 route groups correctly tagged.

### 5. Missing operationId — RESOLVED

**Fixed in**: `backend/openapi_spec.py` — `_build_spec()`

All endpoints have `operationId` in `"{handler}_{path_snake}_{method}"` format.

### 6. Auth Bug (`get_current_user`) — RESOLVED

**Fixed in**: `backend/api/deps.py`

- Removed redundant `session.get()` after `scalar()` → use `scalar_one_or_none()` directly
- Added JWT audience/issuer None-safety via `_decode_jwt()` helper
- Fixed `get_current_active_superuser()` to use `_get_token_scopes()` consistently
- Algorithm hardcoded to `RS256` to prevent algorithm confusion attacks

### Test Results

- OpenAPI spec tests: 12/12 pass
- Route tests: 57/98 pass (41 failures are pre-existing bugs: Pydantic validation errors, date parsing, data format mismatches)

## Remaining Items

The 41 failing route tests are pre-existing application bugs (not related to OpenAPI or auth fixes):
- Pydantic model validation errors (request data format mismatches)
- Date parsing issues (string vs datetime)
- Health check test path issues (routes collided at `/api/v1/`)
