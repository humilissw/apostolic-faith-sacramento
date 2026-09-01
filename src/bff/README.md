# AFC Sacramento — BFF (Backend-For-Frontend)

A thin **Flask** server that sits between the Next.js SPA (`src/fe`) and the
FastAPI backend (`src/be`). The SPA's server-side rendering is not used, so the
browser talks to this BFF with `fetch()` for everything.

The BFF owns authentication **server-side**: the browser never sees a JWT. On
login it authenticates against the backend, keeps the tokens in a signed session
cookie, and hands the SPA a short-lived **one-time auth code** via redirect.
Every `/api/v1/*` request is then forwarded to the backend with the access token
injected as an `Authorization: *** header (with automatic one-shot refresh on 401).

## Why / what it does

- **Server-side login** — `POST /auth/login` → authenticates, stores tokens in a
  signed cookie, redirects the browser to the SPA with `?code=...`.
- **One-time auth code** — the SPA exchanges the code (`POST /auth/session`) to
  confirm who logged in. Codes are single-use and expire after ~2 minutes.
- **Token broker** — access/refresh tokens live only in the BFF session; they are
  never set as browser cookies and never appear in responses.
- **API forwarding** — `/api/v1/<path>` is forwarded verbatim (method, query,
  body, headers) to the backend, with auth injected and a 401→refresh→retry.
- **CORS** — same-site cookie host; echoes the requesting SPA origin and allows
  credentials.

## Tech

- Python 3.12+, **Flask**, **httpx** (hand-rolled forwarding — no reverse-proxy
  library or tunnel middleware).
- Package management: **Poetry**.
- Serves **HTTPS only** (no plain HTTP) on port **8002**.

## Layout

```
src/bff/
├── app/
│   ├── __init__.py      # package marker / version
│   ├── __main__.py      # `python -m app` entrypoint
│   ├── app.py           # Flask app factory + routes (/, /health, /api/v1/*)
│   ├── auth.py          # /auth/* — server-side login, code exchange, me, refresh, logout
│   ├── api.py           # /api/v1/* forwarding + 401 refresh/retry
│   ├── proxy.py         # hand-rolled httpx forwarding to the backend
│   ├── security.py      # one-time auth codes + session token storage helpers
│   ├── cors.py          # CORS headers (no third-party package)
│   └── config.py        # env-driven settings
├── tests/               # pytest suite (mock backend, no network)
├── security_keys/       # self-signed localhost TLS cert (gitignored; see below)
├── pyproject.toml       # Poetry project
├── Dockerfile
├── .env.example
└── README.md
```

## Quick start (local)

Prereqs: Python 3.12+ and [Poetry](https://python-poetry.org/).

```bash
cd src/bff

# 1. Generate a self-signed localhost TLS cert (gitignored; one-time)
mkdir -p security_keys && cd security_keys
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -sha256 -days 3650 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
cd ..

# 2. Install dependencies (Poetry)
poetry install

# 3. Configure
cp .env.example .env   # then set SECRET_KEY and BACKEND_URL as needed
export $(grep -v '^#' .env | xargs)     # or use `direnv` / your shell of choice

# 4. Run (HTTPS on https://localhost:8002)
poetry run python -m app
```

The backend must be reachable at `BACKEND_URL` (default `https://localhost:8000`).
For the self-signed dev backend, set `BACKEND_VERIFY=false` (loopback only).

## Docker

```bash
# From the repo root
docker build -t afc-bff src/bff
docker run --rm -p 8002:8002 \
  -e BACKEND_URL=https://backend:8000 \
  -e BACKEND_VERIFY=false \
  -e SECRET_KEY=*** \
  afc-bff
```

> Docker builds read `security_keys/` from the build context (the filesystem),
> so generate the cert on the host before building even though it is gitignored.

## Endpoints

| Method | Path                     | Description                                                        |
| ------ | ------------------------ | ------------------------------------------------------------------ |
| GET    | `/`                      | Service metadata                                                   |
| GET    | `/health`                | Liveness probe (`{"status":"ok"}`)                                 |
| POST   | `/auth/login`            | Authenticate; **302** redirect to `SPA_URL/?code=<one-time>`       |
| POST   | `/auth/session`          | `{code}` → confirm logged-in user (single-use code)                |
| GET    | `/auth/me`               | Current user (auto-refreshes the access token if needed)           |
| POST   | `/auth/refresh`          | Force a token refresh                                              |
| POST   | `/auth/logout`           | Revoke on backend (best-effort) + clear session                    |
| *      | `/api/v1/<path>`         | Forwarded to the backend with `Authorization: *** injected        |

Login accepts either form-encoded or JSON bodies (`username`/`email` + `password`).

### SPA integration sketch

```ts
// After a redirect lands on the SPA with ?code=...
const code = new URLSearchParams(location.search).get("code");
await fetch(`${BFF}/auth/session`, {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ code }),
});
// From here on, same-origin-ish calls just include the session cookie:
const me = await fetch(`${BFF}/auth/me`, { credentials: "include" });
```

Point the SPA's `NEXT_PUBLIC_API_URL` at the BFF (e.g. `https://localhost:8002/`)
so all existing `/api/v1/*` calls route through it unchanged.

## Configuration

See `.env.example`. Highlights:

- `BACKEND_URL` — upstream FastAPI base URL (default `https://localhost:8000`).
- `BACKEND_VERIFY` — verify backend TLS (`true` default). Set `false` only for a
  self-signed **loopback** dev cert; the BFF refuses to disable verification for
  a non-loopback upstream.
- `SPA_ORIGINS` / `SPA_URL` — allowed SPA origins (CORS) and post-login redirect target.
- `SECRET_KEY` — **required in production**; signs the session cookie + auth codes.
- `AUTH_CODE_TTL_SECONDS` — one-time code lifetime (default 120s).

## Security notes

- Tokens never reach the browser: they are held in a signed, `HttpOnly`,
  `Secure`, `SameSite=Lax` session cookie and forwarded to the backend as a Bearer
  header. The backend's own `Set-Cookie` token cookies are **not** passed through.
- Auth codes are single-use, short-lived, and bound to the issuing session.
- Insecure (unverified) TLS is only permitted against loopback upstream hosts.

## Tests

```bash
cd src/bff
poetry install          # installs dev deps (pytest, etc.)
poetry run pytest
```

The suite uses a mock backend (no network), covering login/code exchange, token
injection, 401 refresh/retry, CORS, and error passthrough.
