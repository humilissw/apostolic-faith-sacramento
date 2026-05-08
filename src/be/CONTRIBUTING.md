# Backend Contributing Guide

## Overview

This is the FastAPI backend for Apostolic Faith Sacramento. Follow these guidelines when contributing to the backend.

## Quick Start for Contributors

```bash
# Clone the repository
git clone <repo-url>
cd apostolic-faith-sacramento/src/be

# Setup development environment
python3 setup_poetry.py
poetry env activate
poetry install

# Verify setup
poetry run pytest
```

## Project Structure

```
be/
├── app/
│   ├── api/
│   │   ├── routes/      # API endpoints
│   │   └── deps.py      # Dependencies (session, user)
│   ├── core/            # Core utilities (db, security)
│   ├── crud.py          # Database CRUD operations
│   ├── models.py        # SQLModel definitions
│   ├── services/        # Business logic layer
│   ├── requests/        # Pydantic request models
│   ├── responses/       # Pydantic response models
│   └── alembic/versions/ # Database migrations
├── tests/               # pytest tests
├── scripts/             # Utility scripts
├── Dockerfile           # Docker configuration
└── pyproject.toml       # Poetry configuration
```

## Development Standards

### 1. Async/Await Pattern

**CRITICAL**: All database operations MUST be async.

```python
# ✅ CORRECT
@router.get("/")
async def get_items(session: SessionDep):
    result = await session.execute(select(Item))
    items = result.scalars().all()
    return items

# ❌ INCORRECT
@router.get("/")
def get_items(session: SessionDep):
    result = session.execute(select(Item))
    items = result.scalars().all()
    return items
```

### 2. Type Hints

All functions must have type hints:

```python
# ✅ CORRECT
async def read_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    current_user: CurrentUser
) -> UserPublic:
    ...

# ❌ INCORRECT
async def read_user(session, user_id, current_user):
    ...
```

### 3. Permission Checks

Always check permissions before allowing access:

```python
@router.get("/{id}")
async def read_item(session: SessionDep, current_user: CurrentUser, id: UUID):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check permissions
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return item
```

### 4. Error Handling

Use descriptive HTTPExceptions with appropriate status codes:

```python
# ✅ CORRECT
if not user:
    raise HTTPException(status_code=404, detail="User not found")

# ❌ INCORRECT
if not user:
    raise HTTPException(status_code=400, detail="User not found")
```

## Making Changes

### Adding a New API Endpoint

1. **Create the route file** in `app/api/routes/`:
   ```python
   from fastapi import APIRouter, Depends
   from app.api.deps import SessionDep, CurrentUser

   router = APIRouter(prefix="/new-resource", tags=["new-resource"])

   @router.get("/")
   async def read_new_resource(session: SessionDep, current_user: CurrentUser):
       ...
   ```

2. **Register the router** in `app/api/main.py`:
   ```python
   from app.api.routes import new_resource

   api_router.include_router(new_resource.router)
   ```

3. **Add database models** in `app/models.py`:
   ```python
   class NewResource(SQLModel, table=True):
       id: str = Field(default_factory=uuid.uuid4, primary_key=True)
       name: str
       created_on: datetime.datetime
   ```

4. **Create CRUD operations** in `app/crud.py`:
   ```python
   async def create_new_resource(
       session: AsyncSession,
       resource_in: NewResourceCreate
   ) -> NewResource:
       resource = NewResource.model_validate(resource_in)
       session.add(resource)
       await session.commit()
       await session.refresh(resource)
       return resource
   ```

5. **Add tests** in `tests/api/routes/test_new_resource.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient

   def test_read_new_resource(client: TestClient, test_token: str):
       response = client.get(
           "/new-resource/",
           headers={"Authorization": f"Bearer {test_token}"}
       )
       assert response.status_code == 200
   ```

### Adding Database Migrations

1. **Update models** in `app/models.py`
2. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "describe your changes"
   ```
3. **Review migration** in `app/alembic/versions/`
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
5. **Test migration**:
   ```bash
   poetry run pytest
   ```

### Writing Tests

Tests should be:

- **Focused**: Test one thing at a time
- **Independent**: Don't rely on test order
- **Real Database**: Use real database connections, not mocks
- **Comprehensive**: Cover success and error cases

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(db_session):
    from app.main import app
    return TestClient(app, headers={"Authorization": f"Bearer {test_token}"})

def test_create_item(client):
    response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "Test description"},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert "id" in data
```

## Code Quality

### Formatting

Run formatters:
```bash
poetry run bash scripts/format.sh
```

### Linting

Run linters:
```bash
poetry run bash scripts/lint.sh
```

### Type Checking

Run mypy:
```bash
poetry run mypy app/
```

### Running All Quality Checks

```bash
poetry run bash scripts/lint.sh
poetry run pytest
poetry run mypy app/
```

## Database Operations

### Async Session Management

```python
# Always use async context manager
async with AsyncSessionLocal() as session:
    # Your database operations here
    result = await session.execute(select(Model))
    await session.commit()
```

### Query Patterns

```python
# Select single item
result = await session.execute(select(User).where(User.id == id))
user = result.scalar_one_or_none()

# Select multiple items
result = await session.execute(select(Item).offset(skip).limit(limit))
items = result.scalars().all()

# Count items
result = await session.execute(select(func.count()).select_from(Model))
count = result.scalar()
```

### CRUD Pattern

```python
async def get_by_id(session: AsyncSession, id: int) -> Model | None:
    result = await session.execute(select(Model).where(Model.id == id))
    return result.scalar_one_or_none()

async def create(session: AsyncSession, model_in: ModelCreate) -> Model:
    model = Model.model_validate(model_in)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model

async def update(
    session: AsyncSession,
    db_model: Model,
    model_in: ModelUpdate
) -> Model:
    update_dict = model_in.model_dump(exclude_unset=True)
    db_model.sqlmodel_update(update_dict)
    session.add(db_model)
    await session.commit()
    await session.refresh(db_model)
    return db_model

async def delete(session: AsyncSession, db_model: Model) -> None:
    session.delete(db_model)
    await session.commit()
```

## Common Pitfalls

### 1. Forgetting await

```python
# ❌ WRONG
result = session.execute(select(Item))

# ✅ CORRECT
result = await session.execute(select(Item))
```

### 2. Mixing sync and async

```python
# ❌ WRONG
@router.get("/")
async def get_items(session: SessionDep):
    # This is sync
    items = session.exec(select(Item)).all()

# ✅ CORRECT
@router.get("/")
async def get_items(session: SessionDep):
    # This is async
    result = await session.execute(select(Item))
    items = result.scalars().all()
```

### 3. Not checking permissions

```python
# ❌ WRONG
@router.get("/{id}")
async def get_item(session: SessionDep, id: UUID):
    return session.get(Item, id)

# ✅ CORRECT
@router.get("/{id}")
async def get_item(session: SessionDep, current_user: CurrentUser, id: UUID):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item
```

## Questions?

- Check [AGENTS.md](./AGENTS.md) for detailed patterns
- Check memory using Claude Code: "check memory"
- Ask in team channels
