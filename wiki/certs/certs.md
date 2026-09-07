# Local Dev TLS Certificates (macOS)

This page explains how the local Docker stack gets its HTTPS certificates, and
how to fix `ERR_CERT_AUTHORITY_INVALID` / "your connection is not private"
errors on a Mac.

## The stack at a glance

All services are served over HTTPS from the docker-compose stack:

| Service          | URL                        | Cert folder                  |
|------------------|----------------------------|------------------------------|
| Backend (FastAPI)| `https://localhost:8000`   | `src/be/security_keys/`      |
| Health edge      | `http://127.0.0.1:8001`    | (plain HTTP readiness only)  |
| BFF (Flask)      | `https://localhost:8002`   | `src/bff/security_keys/`     |
| Frontend (Next)  | `https://localhost:3000`   | `src/fe/security_keys/`      |

Every service certificate is signed by one shared development CA:

- CA cert + key: `infrastructure/certs/ca.pem` / `ca_key.pem` ("AFC Dev CA")
- Each `security_keys/` folder holds that service's leaf key (`cert_key.pem`,
  plus a `key.pem` alias), its chain file (`cert.pem` = leaf + CA), and a copy
  of the CA (`ca.pem`).

These are **development-only** certificates, committed on purpose so a fresh
clone works immediately. Real secret storage is future work — never reuse these
certs or keys outside this repo's local stack.

Notes:

- Certificates identify hostnames, not ports. One cert per service covers
  `localhost`, the Docker DNS names (`backend`, `bff`, `frontend`),
  `host.docker.internal`, and `127.0.0.1` via SANs — so `https://localhost:8000`
  and `https://backend:8000` validate with the same cert.
- Leaf certs are capped at **825 days** validity: Apple's trust engine rejects
  TLS leaf certs valid longer than that, even if the CA is trusted.

## Generating (or regenerating) certificates

From the repo root:

```bash
./infrastructure/generate_dev_certs.sh            # creates anything missing; skips existing
./infrastructure/generate_dev_certs.sh --force    # wipe and regenerate everything
```

After (re)generating, rebuild and restart so containers pick up the new files:

```bash
docker-compose build && docker-compose up -d
```

The script prefers Homebrew OpenSSL (`/opt/homebrew/opt/openssl@3/bin/openssl`)
when installed and otherwise falls back to the system `openssl`. It uses
`-extfile` for extensions because macOS's built-in `/usr/bin/openssl` is
LibreSSL, which does not support `-ext`.

## Fixing "invalid certificate" on a Mac (one-time setup)

A CA-signed chain only stops the browser warnings once **your Mac trusts the
dev CA**. One command does it:

```bash
cd /path/to/apostolic-faith-sacramento
./infrastructure/trust_dev_ca.sh --clean-stale
```

What it does:

1. Generates certs first if they don't exist yet.
2. Installs `infrastructure/certs/ca.pem` as a trusted root:
   - With sudo available → the **admin trust domain**
     (`/Library/Keychains/System.keychain`). This is the most reliable option:
     some Chromium-based browsers ignore per-user trust settings.
   - Without sudo → falls back to your **login keychain** (per-user trust),
     which Safari, curl, and most tools honour. You may see a macOS GUI
     password prompt — enter your login password to approve it.
3. Verifies the install with `security verify-cert`.
4. With `--clean-stale`, finds and deletes old self-signed "localhost"
   certificates/identities left in your login keychain by earlier attempts
   (mkcert, FastAPI docs, etc.). These can shadow the new chain — delete them.

Then **fully quit and relaunch your browser** (Cmd+Q, not just close the
windows). Chromium caches trust state at startup.

### Verify it worked

```bash
# CA trusted by the system:
security verify-cert -c infrastructure/certs/ca.pem -p ssl
# expect: "...certificate verification successful."

# Services load with system trust (no -k / --cacert flags):
curl -s -o /dev/null -w "%{http_code}\n" https://localhost:3000/   # 200
curl -s -o /dev/null -w "%{http_code}\n" https://localhost:8002/   # 200
curl -s -o /dev/null -w "%{http_code}\n" https://localhost:8000/api/v1/health/  # 200
```

In the browser you should see the padlock on `https://localhost:3000`, and the
frontend's calls to the BFF/backend succeed without certificate errors.

## Troubleshooting

**Still ERR_CERT_AUTHORITY_INVALID in Chrome/Vivaldi after trusting:**

1. Fully quit (Cmd+Q) and reopen the browser — trust state is cached per run.
2. Re-run `./infrastructure/trust_dev_ca.sh --clean-stale` to purge stale
   "localhost" identities, then relaunch the browser again.
3. Install into the admin domain (some Chromium builds ignore per-user trust):

   ```bash
   sudo security add-trusted-cert -d -r trustRoot -p ssl \
     -k /Library/Keychains/System.keychain infrastructure/certs/ca.pem
   ```

4. Keychain Access → search "AFC Dev CA" → confirm the cert shows a "+" (trusted).
   If an old AFC CA copy exists with a different serial, delete it and re-run
   the trust script (regenerating certs with `--force` invalidates earlier
   trust settings for the old CA).

**`ERR_CERT_VALIDITY_TOO_LONG`:** your leaf certs predate the 825-day cap —
re-run `./infrastructure/generate_dev_certs.sh --force`, rebuild, restart.

**OpenSSL errors like `unknown option -ext`:** you're on LibreSSL; use the
script (it handles this) rather than hand-rolled openssl commands.

**Container won't start after copying certs in:** the backend Dockerfile chowns
`/app/security_keys` to the runtime user — if you add a new service with certs,
mirror that `chown -R appuser:appuser /app/security_keys` step before `USER`.

**BFF reports SSL error calling backend:** BFF verifies the backend using the CA
bundle mounted from `src/be/security_keys/ca.pem`; after regenerating certs,
restart (`docker-compose up -d`) so the fresh bundle is loaded.

## Files

- `infrastructure/generate_dev_certs.sh` — CA + per-service cert generation
- `infrastructure/trust_dev_ca.sh` — macOS keychain trust installer / repair
- `infrastructure/trustcheck.swift` — browser-grade SecTrust check:
  `swift infrastructure/trustcheck.swift 3000`
