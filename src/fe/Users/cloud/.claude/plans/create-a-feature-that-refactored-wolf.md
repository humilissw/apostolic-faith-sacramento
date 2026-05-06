# JWT Scopes and Claims Implementation

## Context

The app currently has no OAuth2 scope support — authorization is only `is_superuser` boolean. This adds full scope-based JWT claims so:
- Tokens carry `scopes` claim
- Frontend always requests `api:all` scope on login
- Every endpoint requires a token except minimal public endpoints (health checks, Stripe webhook)
- OpenAPI/Swagger shows OAuth2 scopes
- Mobile app scope (`mobile:all`) grants full access

## Minimal Public Endpoints (no token required)
- `/health/*` — health checks
- `/payments/webhook` — Stripe webhook
- `/login/*` — login/refresh/revoke/password-recovery/OAuth
- `/private/*` — local-only dev endpoint

## Implementation

### Phase 1: Backend Foundation

**1. Create `app/core/scopes.py`** — Scope enum:
```python
from enum import Enum

class Scope(str, Enum):
    # Core access scopes
    API_ALL = "api:all"
    SPA_ALL = "spa:all"
    MOBILE_ALL = "mobile:all"
    PUBLIC_READ = "public:read"

    # Payment scopes
    PAYMENTS_READ = "payments:read"
    PAYMENTS_WRITE = "payments:write"
    PAYMENTS_ADMIN = "payments:admin"

    # Integration scopes
    INTEGRATIONS_ADMIN = "integrations:admin"

    # Video upload scopes
    VIDEO_UPLOADS_READ = "video_uploads:read"
    VIDEO_UPLOADS_WRITE = "video_uploads:write"
    VIDEO_UPLOADS_DELETE = "video_uploads:delete"
```

**2. Modify `app/core/security.py`** (line ~109) — add `scopes` to `create_access_token_with_claims()`:
- Add `scopes: list[str] | None = None` parameter
- Add `"scopes": scopes or []` to JWT payload

**3. Modify `app/models.py`** — add `scopes` field to:
- `TokenPayload` (line ~144): `scopes: list[str] | None = None`
- `Token` (line ~135): `scopes: list[str] = Field(default_factory=list)`
- `UpdateTokenResponse` (line ~169): `scopes: list[str] = Field(default_factory=list)`

**4. Modify `app/api/deps.py`** — add scope infrastructure:
- Add `get_current_user_with_scopes()` — returns `tuple[User, list[str]]`
- Add `require_scope(required_scope: str) -> Callable` — dependency factory that checks single scope (superusers bypass)
- Add `require_any_scope(required_scopes: list[str]) -> Callable` — dependency factory that checks any scope
- Register OAuth2 security scheme with FastAPI for OpenAPI:
  ```python
  from fastapi.security import OAuth2
  from fastapi.openapi.models import OAuth2Flows, OAuth2FlowPassword

  oauth2_scheme = OAuth2(
      flows=OAuth2Flows(
          password=OAuth2FlowPassword(
              tokenUrl=f"{settings.API_V1_STR}/login/access-token",
              scopes={s.value: s.value for s in Scope},
          )
      )
  )
  ```

**5. Modify `app/main.py`** (line ~87) — register security scheme:
- After creating `app`, add:
  ```python
  app.security_schemes = {"OAuth2PasswordBearer": oauth2_scheme}
  app.security = [{"OAuth2PasswordBearer": [s.value for s in Scope]}]
  ```

**6. Modify `app/api/routes/login.py`** (line ~48) — read scopes from request:
- Read `form_data.scopes` from `OAuth2PasswordRequestForm`
- For superusers: pass all scope values
- For regular users: pass requested scopes
- Update refresh endpoint too — preserve user's default scopes

**7. Modify `app/api/routes/google.py`** (line ~144) — pass scopes in token creation:
- Superusers get all scopes, regular users get `["api:all"]`

### Phase 2: Route Protection — Add scope dependencies

All non-public endpoints must require a token + scope. Use `dependencies=[Depends(require_scope("..."))]` on each endpoint.

**`app/api/routes/payments.py`:**
| Endpoint | Scope |
|---|---|
| POST `/create-intent` | `payments:write` |
| POST `/create-subscription` | `payments:write` |
| POST `/webhook` | **no scope** (public) |
| GET `/` | `payments:read` |
| GET `/config` | **no scope** (public) |
| GET `/{payment_id}` | `payments:read` |

**`app/api/routes/integrations.py`:**
| Endpoint | Scope |
|---|---|
| GET `/` | `integrations:admin` |
| GET `/status` | **no scope** (public) |
| GET `/{id}` | `integrations:admin` |
| POST `/` | `integrations:admin` |
| PUT `/{id}` | `integrations:admin` |
| PATCH `/{id}/credentials` | `integrations:admin` |
| DELETE `/{id}` | `integrations:admin` |
| POST `/test-connection` | `integrations:admin` |
| POST `/sync-status/{id}` | `integrations:admin` |
| POST `/pre-seed` | `integrations:admin` |

**`app/api/routes/video_uploads.py`:**
| Endpoint | Scope |
|---|---|
| GET `/liveness`, `/readiness` | **no scope** (public) |
| GET `/` | `video_uploads:read` |
| GET `/{id}` | `video_uploads:read` |
| POST `/` | `video_uploads:write` |
| PATCH `/{id}` | `video_uploads:write` |
| DELETE `/{id}` | `video_uploads:delete` |

**`app/api/routes/media.py`:**
| Endpoint | Scope |
|---|---|
| GET `/liveness`, `/readiness` | **no scope** (public) |
| All other endpoints | `api:all` |

**`app/api/routes/items.py`:** All endpoints → `api:all`

**`app/api/routes/users.py`:**
| Endpoint | Scope |
|---|---|
| `/signup` | **no scope** (public) |
| All other endpoints | `api:all` |

**`app/api/routes/church_services.py`, `announcements.py`, `members.py`:** All endpoints → `api:all`

### Phase 3: Frontend

**15. Modify `src/fe/lib/api.ts`** — update `login()` and `fetchWithAuth()`:
- Add `scopes: string[]` to `LoginResponse` interface
- Add `scopes: string[] = ["api:all"]` parameter to `login()`
- Append `scope: scopes.join(" ")` to form data
- Fix `fetchWithAuth()` to always inject `Authorization: Bearer <token>` header

**16. Modify `src/fe/context/auth-context.tsx`** — store scopes:
- Add `scopes: string[]` to context interface
- Store scopes in localStorage as `"auth_scopes"`
- Add `hasScope(requiredScope: string)` helper to context

**17. Modify `src/fe/app/(auth)/login/page.tsx`** — pass scope:
- Call `apiLogin(email, password, ["api:all"])`
- Pass scopes to login context callback

**18. Create `src/fe/components/scope-guard.tsx`** — new guard component:
- Accepts `requiredScopes: string[]` prop
- Checks `hasScope()` for each required scope
- Redirects to login if unauthenticated, or "/" if missing scopes

**19. Modify `src/fe/components/superuser-guard.tsx`** — extract scopes from JWT:
- Add `scopes` to decoded payload return type

### Phase 4: Testing

**20. Update `src/be/tests/conftest.py`** — add scopes to test token fixtures

**21. Update `src/be/tests/api/routes/login_test.py`** — test scopes in token response

**22. Update `src/be/tests/api/routes/scopes_test.py`** — create comprehensive scope tests

**23. Run all tests and pre-commit hooks**

## Verification
1. `poetry run pytest` — all 143 backend tests pass
2. `pnpm test` — all 99 frontend tests pass
3. Pre-commit hooks pass (mypy, black, ruff, bandit, editorconfig-checker)
4. Swagger UI shows "Authorize" button with all scopes listed
5. Login endpoint returns `scopes` array in response
6. Protected endpoints return 403 without valid scope
