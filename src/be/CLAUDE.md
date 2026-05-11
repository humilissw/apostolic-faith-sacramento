# Backend CLAUDE.md

## Project Overview

A FastAPI backend for the Apostolic Faith Sacramento church application. Currently on `feature/media-page-functionality` branch working on video/media upload capabilities.

## Quick Start

```bash
# Setup
python3 setup_poetry.py
poetry env activate
poetry install

# Run locally
poetry run fastapi dev main.py

# Run tests
poetry run pytest

# Format code
poetry run bash scripts/format.sh

# Lint code
poetry run bash scripts/lint.sh
```

## Key Files

- `app/models.py` - SQLModel definitions (database schema)
- `app/api/routes/*.py` - API endpoints
- `app/api/deps.py` - Dependency injection (session, user)
- `app/core/db.py` - Database configuration
- `app/core/security.py` - Password hashing, JWT
- `app/crud.py` - CRUD operations
- `app/config.py` - Configuration with pydantic-settings
- `app/services/` - Business logic layer
- `alembic/` - Database migrations
- `tests/` - pytest tests

## Architecture Patterns

### API Route Pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import SessionDep, CurrentUser
from app.models import Model, ModelCreate, ModelUpdate, ModelPublic
from app.crud import crud_model

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/", response_model=ModelsPublic)
async def read_models(session: SessionDep, skip: int = 0, limit: int = 100):
    """List models with pagination."""
    if current_user.is_superuser:
        # Superuser logic
    else:
        # Regular user logic
    return ModelsPublic(data=items, count=count)

@router.post("/")
async def create_model(*, session: SessionDep, model_in: ModelCreate):
    """Create new model."""
    model = await crud.create_model(session=session, model_in=model_in)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model
```

### Async Session Usage

```python
# Always use await for database operations
@router.get("/")
async def get_data(session: SessionDep):
    # Execute query
    result = await session.execute(select(Model))
    items = result.scalars().all()

    # Update and commit
    item = session.get(Model, id)
    item.name = "new name"
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
```

### SQLModel Pattern

```python
# Base model for shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

# Database table
class Item(ItemBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    owner_id: int = Field()
    created_on: datetime.datetime

# API response (exclude internal fields)
class ItemPublic(ItemBase):
    id: int
    owner_id: int
```

## Database

- **Engine**: MySQL with asyncmy driver
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Migrations**: Alembic
- **Connection**: AsyncSession from `app.core.db`

Run migrations:
```bash
alembic upgrade head
```

## Authentication

- JWT tokens in Authorization header
- `CurrentUser` dependency validates tokens
- Superuser check: `current_user.is_superuser`
- Password hashing with bcrypt

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run bash scripts/test.sh

# Test structure
tests/
├── conftest.py      # Fixtures
├── api/routes/      # Route tests
└── crud/            # CRUD tests
```

## Development

- Python 3.13+
- FastAPI (0.114.2+)
- SQLAlchemy 2.0.45+
- SQLModel 0.0.21+
- Poetry for dependency management

## Gotchas

1. Always use `await session.execute(select(Model))`
2. Use `.scalars().all()` for multiple results
3. Use `.scalar()` for single result
4. Always `await session.commit()` after mutations
5. Always `await session.refresh(obj)` after commit
6. Use `new_id` (UUID) and `id` (int) together
7. Check permissions before allowing access

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [AGENTS.md](./AGENTS.md) - Detailed agent guide
