---
name: project-setup
description: Information about how the project was initialized and key setup steps
type: project
---

# Project Setup

**Date**: 2026-04-12 (updated 2026-08-06)

## Initialization

This is a multi-platform application for Apostolic Faith Sacramento church, consisting of:
- **Backend**: FastAPI (Python) — REST API at `src/be/`
- **Frontend**: Next.js 16 (App Router) — Web app at `src/fe/`
- **Mobile**: Expo SDK 56 (React Native) — Mobile app at `src/afc-mobile/`

## Key Setup Commands

### Backend (Poetry)
```bash
cd src/be
python3 setup_poetry.py
poetry env activate
poetry install
poetry run fastapi dev main.py
```

### Frontend (bun)
```bash
cd src/fe
bun install
bun dev
```

### Mobile (pnpm)
```bash
cd src/afc-mobile
pnpm start
```

### Docker
```bash
docker-compose up -d
```

## Project Structure

- **Backend**: `src/be/` — FastAPI + SQLModel + MySQL (asyncmy)
- **Frontend**: `src/fe/` — Next.js 16 + TypeScript + Tailwind CSS v4 + bun
- **Mobile**: `src/afc-mobile/` — Expo SDK 56 + React Native + pnpm

## Important Files

- `src/be/pyproject.toml` — Poetry project configuration
- `src/be/.env` — Environment variables (local, never commit)
- `src/fe/package.json` — Frontend dependencies
- `src/fe/.env.local` — Frontend environment overrides
- `docker-compose.yml` — Local development stack

## SSL Certificates

Required for production: `infrastructure/certs/cert.pem` and `key.pem`

## How to Apply

- When starting work: Check this file for initial setup commands
- When making changes: Reference the structure and dependencies in each component's pyproject.toml/package.json
- When deploying: Use Docker or follow individual component commands
