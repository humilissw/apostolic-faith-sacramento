# Node.js Hosting deploy contract

contractVersion: 3

Testable rules for apps deployed on GoDaddy Node.js Hosting (PaaS). Enforced by [scripts/validate-paas.mjs](scripts/validate-paas.mjs) where noted.

## Deploy pipeline

1. Root `package.json` exists with `name`, `version`, and `main`.
2. `scripts.build` and `scripts.start` are present and non-empty.
3. Platform runs: **production install** (omits `devDependencies`) → **`run build`** → **`run start`** (npm, pnpm, or yarn from lockfile or `packageManager`).
4. Upload includes a lockfile when possible: `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`.
5. Do **not** upload `node_modules` — production install omits `devDependencies`; runtime packages must be in `dependencies`.

## Application rules

| ID | Rule | Validator |
|----|------|-----------|
| C1 | Single app per upload; monorepos must extract one app folder with its own root `package.json`. | — |
| C2 | `package.json` has non-empty `name`, `version`, and `main`; `main` file exists. | E007, E008 |
| C3 | `scripts.build` always defined (no-op e.g. `echo build` is OK if nothing compiles). | E005 |
| C4 | `scripts.start` defined; entry file exists when `start` is `node <file>`. | E002, E003 |
| C5 | Listen using `process.env.PORT` (fallback `3000` locally is OK). | E004 |
| C6 | No hardcoded listen ports in server/entry source. | E004 |
| C7 | When a framework needs a host, bind `0.0.0.0` (not `localhost` only). | — |
| C8 | Secrets and config via `process.env`; no `.env` in upload. | W001 |
| C9 | Vite: platform updates allowed-hosts; dev/preview must respect `PORT`. | — |
| C10 | Upload zip under 100 MB; exclude `node_modules`, caches, large artifacts. | W004 |
| C11 | Outbound: HTTP (80), HTTPS (443), and GoDaddy managed MySQL only. | — |
| C12 | If using DB: read `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` from `process.env`; use `mysql2` in `dependencies` and parameterized queries. External DBs on non-80/443 are not reachable. | E009, E010 |

## Framework build hints

When these dependencies are present, `scripts.build` must run a real compile step (not only `echo build`):

| Dependency signal | Typical `build` |
|-------------------|-----------------|
| `next` | `next build` |
| `nuxt` | `nuxt build` |
| `@remix-run/*` | `remix build` |
| `@nestjs/core` | `nest build` |
| `vite` (SPA) | `vite build` |
| `react-scripts` | `react-scripts build` |

## Runtime dependency heuristic

These must not appear only in `devDependencies` if required at runtime:

`express`, `fastify`, `koa`, `hono`, `@hono/node-server`, `next`, `nuxt`, `@nestjs/core`, `@remix-run/serve`, `remix-serve`

## Validator message IDs

| ID | Meaning |
|----|---------|
| E001 | Missing or invalid root `package.json` |
| E002 | Missing or empty `scripts.start` |
| E003 | Start script entry file not found |
| E004 | Hardcoded port in source |
| E005 | Missing or empty `scripts.build` |
| E006 | Runtime package in `devDependencies` |
| E007 | Missing or empty `name` or `version` |
| E008 | Missing, invalid, or missing file for `main` |
| W001 | `.env` file present in project |
| W002 | Missing `engines.node` |
| W003 | Could not verify start script target |
| W004 | `node_modules` present (exclude from deployment) |
| E009 | Database use without `mysql2` in `dependencies` |
| E010 | Missing `process.env` reference for a required `DB_*` variable |
