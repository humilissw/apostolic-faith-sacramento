# Apostolic Faith Sacramento - CLAUDE.md

## Project Overview

A multi-platform application for the Apostolic Faith Sacramento church, including:
- **Backend**: FastAPI (Python) - REST API
- **Frontend**: Web application
- **Mobile**: Mobile application

## Quick Navigation

### Backend
- **Path**: `/src/be/`
- **CLAUDE.md**: See [be/CLAUDE.md](./src/be/CLAUDE.md)
- **AGENTS.md**: See [be/AGENTS.md](./src/be/AGENTS.md)

### Frontend
- **Path**: `/src/fe/`
- **CLAUDE.md**: See [fe/CLAUDE.md](./src/fe/CLAUDE.md)
- **AGENTS.md**: See [fe/AGENTS.md](./src/fe/AGENTS.md)

### Mobile
- **Path**: `/src/mobile/`
- **CLAUDE.md**: See [mobile/CLAUDE.md](./src/mobile/CLAUDE.md)

## Project Structure

```
apostolic-faith-sacramento/
├── .claude/
│   └── memory/
│       ├── MEMORY.md              # Memory index
│       ├── project/               # Project memories
│       ├── feedback/              # Feedback guidelines
│       └── reference/             # Reference documentation
├── infrastructure/
│   ├── certs/                     # SSL certificates
│   └── DOCKER_DEPENDENCIES.md
├── src/
│   ├── be/                        # Backend
│   ├── fe/                        # Frontend
│   └── mobile/                    # Mobile
└── README.md                      # Root documentation
```

## Development Setup

### SSL Certificates (required for production)

**Mac/Linux**:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost"
```

**Windows** (using mkcert):
```powershell
mkcert -install
mkcert -key-file key.pem -cert-file cert.pem localhost
```

## CLAUDE Memory System

This project uses Claude's memory system to track important information:

- **User memories** - User roles, preferences, knowledge
- **Feedback memories** - What to avoid and what to keep doing
- **Project memories** - Current work, goals, incidents
- **Reference memories** - External resources and file pointers

Access memory from Claude Code by asking "check memory" or specific requests like "check feedback for testing".

## Development Workflow

1. **Check memory** - Always start by checking relevant memory files
2. **Read CLAUDE.md** - Check the specific CLAUDE.md for the component you're working on
3. **Use AGENTS.md** - Detailed patterns and conventions
4. **Run tests** - Ensure tests pass before committing
5. **Format and lint** - Use scripts to maintain code quality
6. **Commit** - Follow commit message conventions

## Getting Started with Claude Code

When working with this project:

1. Ask "tell me about this project" for an overview
2. Ask "check memory" for stored information
3. Ask "check feedback" for coding guidelines
4. Ask "show me the API" for endpoint documentation
5. Ask "what's on the current branch" for recent changes

## Common Commands

### Backend
```bash
cd src/be
python3 setup_poetry.py
poetry install
poetry run fastapi dev main.py
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f
docker-compose test
```

### Frontend
```bash
cd src/fe
pnpm install
pnpm dev          # run dev server
pnpm build        # static export
pnpm test         # run tests
pnpm lint         # lint code
```

### Testing
```bash
# Backend
cd src/be
poetry run pytest

# Frontend
cd src/fe
pnpm test

# Full stack
docker-compose test
```

## Important Notes

- SSL certificates required for production deployment
- Never commit `.env` or `.env.prod` files
- Use environment variables for sensitive data
- Database migrations must be run before starting the app
- All database operations must use async/await
