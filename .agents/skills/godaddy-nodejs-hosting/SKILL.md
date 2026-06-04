---
name: godaddy-nodejs-hosting
description: >-
  Scaffolds and adapts Node.js apps for GoDaddy Node.js Hosting (PaaS): package.json
  start/build scripts, PORT binding, single-app upload, framework recipes. Use when
  building a new app, adapting an existing app, fixing deploy or start failures,
  or preparing AI tool exports (Replit, Lovable, Bolt, Cursor) for Node.js Hosting.
disable-model-invocation: true
---

# GoDaddy Node.js Hosting

Help users build or fix Node.js apps for **GoDaddy Node.js Hosting** (upload → install → `run build` → `run start`). Package manager: **npm**, **pnpm**, or **yarn** (lockfile determines platform choice).

Rules: [contract.md](contract.md). Recipes: [examples.md](examples.md). Errors: [troubleshooting.md](troubleshooting.md). Validator: [scripts/validate-paas.mjs](scripts/validate-paas.mjs).

## When to use which path

| User intent | Section |
|-------------|---------|
| New app / scaffold / greenfield | [New app workflow](#new-app-workflow) |
| Existing repo / deploy failed / make this work on hosting | [Adapting an existing app](#adapting-an-existing-app) |
| AI export (Lovable, Replit, Bolt, etc.) | [Adapting an existing app](#adapting-an-existing-app) + [AI export quick fixes](#ai-export-quick-fixes) |
| Uses MySQL / database on platform | [Managed MySQL](#managed-mysql) |

## Audience routing

**Non-technical user** (no jargon, “I built this in Lovable”, “how do I upload”):

1. Output the [pre-upload checklist](#pre-upload-checklist) first in plain language.
2. Follow [Adapting an existing app](#adapting-an-existing-app) (existing zip or export).
3. Prefer the [static SPA + Express](examples.md#vite-react-vue-spa) or [static only](examples.md#static-only) recipe when there is no server.
4. One small change at a time; explain the next hosting step in plain language (Git sync or zip upload in the UI).
5. Run the validator before saying the app is ready.

**Technical user - existing app**: follow [Adapting an existing app](#adapting-an-existing-app); use the matching framework recipe for `start`/`build` only; do not re-explaining basics.

**Technical user - new app**: follow [New app workflow](#new-app-workflow); use the matching framework recipe from [Framework detection](#framework-detection).

## Deploy contract (summary)

- Root `package.json` with `name`, `version`, `main` (file exists), `scripts.build`, and `scripts.start`
- `build` may be `"echo build"` when nothing compiles; frameworks need real build commands ([examples.md](examples.md))
- Listen on `process.env.PORT`; use `0.0.0.0` when the framework needs a host
- Runtime deps in `dependencies`; do not upload `node_modules`
- Secrets via `process.env`; no `.env` in zip; zip under 100 MB
- One app per upload; lockfile when possible
- Outbound HTTP/HTTPS only; platform MySQL via `DB_*` env + `mysql2` if using a database ([contract.md](contract.md))

## Publishing updates (customer communication)

The platform supports **Git repository sync** and **zip upload** in the Node.js Hosting UI. See [AGENTS.md](../../AGENTS.md) Deployment Flow for agent context.

- **Do not infer** deploy method from `.git`, lockfiles, or export origin (a zip export may include `.git` from local development).
- **Default when telling the user how to publish:** use neutral wording — e.g. *“When you’re ready, update the app in Node.js Hosting using Git sync or a zip upload in the hosting UI.”*
- **Only go path-specific** (zip steps vs connect/push Git) if the user **states or asks** which they use.
- **Avoid** prescriptive one-path phrases like “upload a new zip” or “push to your remote” without that confirmation.

## Managed MySQL

Optional platform MySQL injects `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. The app must read each from `process.env` (not hard-coded). Use **`mysql2`** in `dependencies` and parameterized queries.

Recipe: [examples.md#managed-mysql](examples.md#managed-mysql). Validator: **E009**, **E010** when a DB client or Prisma MySQL provider is detected.

## Adapting an existing app

Use this path when the user already has a project (local repo, zip export, or app that failed on Node.js Hosting). Goal: **hosting compatibility only** — not new features, refactors, or framework changes.

### Principles

- Do not add or remove product features; do not refactor unrelated code.
- Smallest diff: prefer `package.json` (`name`, `version`, `main`, `build`, `start`), listen/bind lines, and a static server file when missing — not rewriting app logic.
- Keep the detected framework; align `main`, `scripts.start`, and `scripts.build` with [examples.md](examples.md) for that stack only.

### Adaptation workflow

Audit against [contract.md](contract.md) (nine platform requirements: `package.json` fields, `build`/`start`, PORT, deps, env vars, Vite, zip size, network, MySQL). For each item: check compliance, apply the smallest fix, preserve all existing behaviour.

Copy and track progress:

```
- [ ] Run validator on project root (baseline)
- [ ] Map each error/warning to contract rule (see table below)
- [ ] Apply minimal fix per ID; use framework recipe for script names only
- [ ] Re-run validator until exit 0 (or document warnings if not --strict)
- [ ] install → build → start locally (match lockfile package manager)
- [ ] Pre-upload checklist complete
```

**Validator** (required before done):

```bash
node scripts/validate-paas.mjs /path/to/project
```

Run from this skill directory (e.g. after `npx skills add` or symlink to `~/.cursor/skills/godaddy-nodejs-hosting`). From a clone of [nodejs-hosting-agent-skill](https://github.com/godaddy/nodejs-hosting-agent-skill): `npm run validate -- /path/to/project`.

Symptom detail: [troubleshooting.md](troubleshooting.md).

| ID | Typical minimal fix |
|----|---------------------|
| E001 | Add root `package.json` |
| E002 | Add or fix `scripts.start` per recipe |
| E003 | Fix `start` entry path or add missing file |
| E004 | Use `process.env.PORT`; remove hardcoded `listen(N)` |
| E005 | Add `scripts.build` (`echo build` or framework recipe) |
| E006 | Move runtime packages to `dependencies` |
| E007 | Add `name` and `version` to `package.json` |
| E008 | Add `main` pointing at an existing entry file |
| W001 | Remove `.env` from upload; use hosting UI for env vars |
| W002 | Optional: add `engines.node` |
| W004 | Exclude `node_modules` from deployment (zip or Git) |
| E009 | Add `mysql2` to `dependencies` |
| E010 | Read each `DB_*` from `process.env` (see [managed-mysql](examples.md#managed-mysql)) |

**Special cases**

- **Monorepo (C1):** extract a single app folder with its own root `package.json` before adapting; do not restructure packages in place unless the user asks.
- **Frontend-only / no server:** [vite-react-vue-spa](examples.md#vite-react-vue-spa) and [AI export quick fixes](#ai-export-quick-fixes).
- **Migrating from another host:** same steps; focus on `PORT`, `start`/`build`, `dependencies`, and lockfile.

For Replit, Lovable, and Bolt patterns, see [AI export quick fixes](#ai-export-quick-fixes) after applying this workflow.

Adaptation is complete under the same [done criteria](#done-criteria) as a new app (validator `0`, checklist, ready to update in Node.js Hosting).

## New app workflow

Copy and track progress:

```
- [ ] Detect framework (package.json)
- [ ] Apply recipe from examples.md
- [ ] install && run build (if exists) && run start (npm, pnpm, or yarn — match user's lockfile)
- [ ] node scripts/validate-paas.mjs <project-dir>
- [ ] Pre-upload checklist complete
```

Run the validator as in [Adapting an existing app](#adapting-an-existing-app).

## Framework detection

| Signal in `package.json` | Recipe |
|--------------------------|--------|
| `next` in dependencies | [examples.md#nextjs](examples.md#nextjs) |
| `nuxt` in dependencies | [examples.md#nuxtjs](examples.md#nuxtjs) |
| `@remix-run/node` or `remix` | [examples.md#remix](examples.md#remix) |
| `@nestjs/core` | [examples.md#nestjs](examples.md#nestjs) |
| `fastify` | [examples.md#fastify](examples.md#fastify) |
| `vite` (SPA) | [examples.md#vite-react-vue-spa](examples.md#vite-react-vue-spa) |
| `react-scripts` | [examples.md#create-react-app](examples.md#create-react-app) |
| `express`, `koa`, `hono` or plain `node` server | [examples.md#express-koa-hono](examples.md#express-koa-hono) |
| Frontend-only / unknown export | [examples.md#vite-react-vue-spa](examples.md#vite-react-vue-spa) (static server) |

Do not invent `start` commands for known frameworks; use the recipe exactly.

## AI export quick fixes

| Source | Fix |
|--------|-----|
| Replit | Remove `.replit`, `replit.nix`; ensure root `start` script |
| Lovable / Bolt | Add Express static server for `dist/` or `build/`; add `express` to `dependencies` |
| Missing `package.json` | Create with `start`; run install (npm/pnpm/yarn) to generate lockfile |
| Hardcoded port | Use `process.env.PORT \|\| 3000` |
| Wrong deps section | Move runtime packages to `dependencies` |

For Lovable/Bolt static hosting, use the [vite-react-vue-spa](examples.md#vite-react-vue-spa) recipe.

## Pre-upload checklist

- [ ] `package.json`: `name`, `version`, `main`, `build`, `start`
- [ ] Production deps in `dependencies`; do not deploy `node_modules` (exclude from zip or Git)
- [ ] `process.env.PORT` for listening; secrets via `process.env`
- [ ] Deployment artifact under 100 MB (zip upload)
- [ ] Runs locally: install → build → start
- [ ] Lockfile present (committed or included in upload); validator exit 0; no `.env`
- [ ] HTTP/HTTPS outbound only; DB uses `DB_*` + `mysql2` if applicable

## Done criteria

Task is complete only when:

1. `validate-paas.mjs` exits `0` on the project directory.
2. Pre-upload checklist is satisfied.
3. User knows they can publish/update the app in Node.js Hosting (Git sync or zip upload in the UI). Mention only the path they use if they’ve already said so.
