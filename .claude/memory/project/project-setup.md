---
name: project-setup
description: Information about how the project was initialized and key setup steps
type: project
---

# Project Setup

**Date**: 2026-04-12

## Initialization

This is the Apostolic Faith Sacramento backend project, a FastAPI application for managing church operations including members, services, items, and media uploads.

## Key Setup Commands

### Poetry Setup
```bash
# Mac/Linux
python3 setup_poetry.py
poetry env activate
poetry install

# Run the app
poetry run fastapi dev main.py
```

### Docker Setup
```bash
docker-compose up -d
```

## Project Structure

- **Backend**: `/Users/cloud/code/apostolic-faith-sacramento/src/be/`
- **Frontend**: `/Users/cloud/code/apostolic-faith-sacramento/src/fe/`
- **Mobile**: `/Users/cloud/code/apostolic-faith-sacramento/src/mobile/`

## Current Branch

`feature/media-page-functionality` — Working on video/media upload functionality

## Recent Commits

- Add ability to upload videos
- Fix async/await session issues
- Add media tables to database

## Important Files

- `pyproject.toml` — Poetry project configuration
- `uv.lock` — uv package lock file
- `Dockerfile` — Docker container configuration
- `alembic.ini` — Alembic migration configuration
- `.env` — Environment variables (local)
- `.env.prod` — Environment variables (production)

## SSL Certificates

Required for production: `../../infrastructure/certs/cert.pem` and `key.pem`

## How to Apply

- When starting work: Check this file for initial setup commands
- When making changes: Reference the structure and dependencies in pyproject.toml
- When deploying: Use Docker or follow poetry commands in README.md
