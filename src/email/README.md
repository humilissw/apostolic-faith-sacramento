# AFC Email Microservice (src/email/)

Email delivery microservice for Apostolic Faith Sacramento. The backend
(`src/be/`) no longer talks to SMTP itself — it delegates every email to this
service over HTTP.

## Responsibilities

- Deliver templated emails: `password-reset`, `new-user`, `announcement`,
  `assignment`, `test`.
- Track every delivery attempt in its **own** database (SQLite by default,
  `TRACKING_DB_URL`) so the service stays self-contained for email delivery.
- Read recipients from the **shared application database** (`users` table) —
  read-only, until user management is extracted into its own microservice.

## Auth model

- The email service **never issues tokens**. It verifies RS256 JWTs issued by
  `src/be/` using that service's public key (`RSA_PUB_KEY`).
- Every send request must carry the `api:email` scope (superuser tokens also
  qualify). Add the scope to a user via the backend user-management API.
- Server-to-server calls that cannot present a user JWT (e.g. the
  unauthenticated password-recovery flow) may use `X-API-Key: <SERVICE_API_KEY>`.

## API

```
POST /api/v1/email/send
Authorization: Bearer <jwt with api:email scope>   # or X-API-Key

{ "type": "password-reset", "recipients": ["a@b.org"], "token": "<signed link token>" }
{ "type": "new-user",       "recipients": ["new@b.org"], "token": "<signed link token>" }
{ "type": "announcement",   "body": "Service is at 7pm Sunday." }        # all active users
{ "type": "announcement",   "body": "...", "recipients": ["x@y.org"] }   # targeted
{ "type": "assignment",     "recipients": [...], "assignment_type": "music",
                            "role": "drummer", "event_date": "2026-09-20" }
{ "type": "test",           "recipients": ["dev@b.org"] }
```

Reset/set-up links embed the `token` exactly as provided: token generation and
verification stay entirely in `src/be/`.

## Running locally

```bash
cd src/email
python3.12 -m venv .venv && .venv/bin/pip install -e ".[test]"
cp .env.local .env     # local dev values (git-ignored; see .env.example for all keys)
cp ../be/security_keys/public_key.pem security_keys/  # if not present
.venv/bin/python -m uvicorn app.main:app --port 8100
.venv/bin/python -m pytest
```

In docker-compose the service runs as `email` on port 8100 with SMTP pointed at
mailcatcher for local testing (web UI: http://localhost:1080).

## Configuration layering

- `.env.example` — REQUIRED by docker-compose; documents every key and holds
  safe container defaults (mailcatcher SMTP, `database` host, no creds).
- `.env.local` / `.env.prod` — git-ignored overlays with real values. When
  `ENVIRONMENT=local|development|dev`, `app/config.py` also loads `.env.local`;
  when `ENVIRONMENT=production|prod`, it loads `.env.prod`. A plain `.env`
  always applies if present (later files win; real env vars beat all).
- Production deploys provide `.env.prod` and set `ENVIRONMENT=production`.
