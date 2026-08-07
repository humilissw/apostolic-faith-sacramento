# AGENTS.md

High-level overview of the Apostolic Faith Sacramento backend project and development patterns.

## Project Overview

A FastAPI backend for the Apostolic Faith Sacramento church application, serving members, managing church services, and handling media uploads.

**Current Branch**: `main` (production-ready, deployed to Vercel)

## Architecture

### Tech Stack
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MySQL with asyncmy driver
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Auth**: JWT tokens + password hashing (bcrypt)
- **Package Management**: Poetry
- **Containerization**: Docker
- **Migrations**: Alembic
- **Testing**: pytest
- **Email**: MJML templates with Jinja2

### Project Structure

```
be/
├── app/
│   ├── api/
│   │   ├── routes/          # Endpoint definitions
│   │   │   ├── announcements.py     # Church announcements
│   │   │   ├── church_services.py   # Service records
│   │   │   ├── client_credentials.py  # OAuth2 client management
│   │   │   ├── feature_flags.py     # Feature flag endpoints
│   │   │   ├── google.py            # Google OAuth integration
│   │   │   ├── health.py            # Health check
│   │   │   ├── integrations.py      # Third-party integrations
│   │   │   ├── items.py             # Generic item management
│   │   │   ├── login.py             # Authentication endpoints
│   │   │   ├── media.py             # Media file management
│   │   │   ├── members.py           # Member profiles
│   │   │   ├── payments.py          # Donations and payments (Stripe)
│   │   │   ├── private.py           # Local-only routes
│   │   │   ├── scheduler.py         # Church scheduler endpoints
│   │   │   ├── user_scopes.py       # User permission scopes
│   │   │   ├── users.py             # User CRUD
│   │   │   └── video_uploads.py     # Video upload tracking
│   │   ├── deps.py          # Dependency injection (SessionDep, CurrentUser)
│   │   └── main.py          # API router aggregation
│   ├── core/
│   │   ├── db.py              # Database session management
│   │   ├── logging.py         # Logging configuration
│   │   ├── rate_limiter.py    # Rate limiting middleware
│   │   ├── result.py          # Unified result pattern
│   │   ├── scopes.py          # Permission scope definitions
│   │   └── security.py        # Password hashing, JWT
│   ├── crud.py              # Database CRUD operations
│   ├── models.py            # SQLModel definitions
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── church_meeting_service.py
│   │   ├── feature_flag_service.py
│   │   ├── integration_service.py
│   │   ├── media_service.py
│   │   ├── payment_service.py
│   │   └── scheduler_service.py
│   ├── repositories/        # Data access layer
│   │   ├── assignment_repo.py
│   │   ├── feature_flag_repo.py
│   │   ├── integration_repo.py
│   │   ├── media_repo.py
│   │   ├── payment_repo.py
│   │   ├── user_repo.py
│   │   ├── user_scope_repo.py
│   │   └── video_upload_repo.py
│   ├── requests/            # Pydantic request models
│   ├── responses/           # Pydantic response models
│   ├── alembic/versions/    # Database migrations
│   ├── email-templates/     # MJML email templates
│   └── initial_data.py      # Seed data
├── tests/                   # pytest tests
├── scripts/                 # Shell scripts (prestart, format, lint)
└── Dockerfile              # Docker configuration
```

## Development Patterns

### 1. API Route Structure

Each route file follows this pattern:

```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import SessionDep, CurrentUser
from app.models import Model, ModelCreate, ModelUpdate, ModelPublic
from app.crud import crud_model

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/", response_model=ModelsPublic)
async def read_models(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
):
    """List models with pagination and permission checking."""
    if current_user.is_superuser:
        # Superuser gets all records
        count_statement = select(func.count()).select_from(Model)
        count = session.exec(count_statement).one()
        statement = select(Model).offset(skip).limit(limit)
    else:
        # Regular users see only their own records
        count_statement = select(func.count()).where(Model.owner_id == current_user.id)
        count = session.exec(count_statement).one()
        statement = select(Model).where(Model.owner_id == current_user.id)
    return ModelsPublic(data=session.exec(statement).all(), count=count)

@router.get("/{id}", response_model=ModelPublic)
async def read_model(session: SessionDep, current_user: CurrentUser, id: UUID):
    """Get a single model by ID with permission checking."""
    model = session.get(Model, id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if not current_user.is_superuser and model.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return model
```

### 2. SQLModel Model Patterns

Use inheritance hierarchy for clean API responses:

```python
# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

# For database table
class Item(ItemBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    owner_id: int = Field()
    created_on: datetime.datetime
    updated_on: datetime.datetime | None = None

# For API responses (exclude internal fields)
class ItemPublic(ItemBase):
    id: int
    owner_id: int
```

### 3. Authentication & Authorization

**JWT Token Flow**:
1. Login → `/login/access-token` → receives access token
2. Include token in `Authorization: Bearer <token>` header for protected routes
3. `CurrentUser` dependency validates and injects user into route handler

**Permissions**:
- `current_user.is_superuser` - full access to all resources
- Regular users only access their own records (checked via `owner_id`)

### 4. Database Access

**Async Sessions**:
```python
# Database configuration in app/core/db.py
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

**Using Async Sessions in Routes**:
```python
# In routes - execute queries with await
@router.get("/")
async def read_users(session: SessionDep, skip: int = 0, limit: int = 100):
    # Execute query and get count
    count_statement = select(func.count()).select_from(User)
    count_result = await session.execute(count_statement)
    count = count_result.scalar()

    # Execute query for data
    statement = select(User).offset(skip).limit(limit)
    users_result = await session.execute(statement)
    users = users_result.scalars().all()

    return UsersPublic(data=users, count=count)

@router.post("/")
async def create_user(*, session: SessionDep, user_in: UserCreate):
    # Check for existing user
    user = await crud.get_user_by_email(session=session, email=user_in.email)

    # Create new user
    user = await crud.create_user(session=session, user_create=user_in)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.patch("/me")
async def update_user_me(*, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser):
    # Update user fields
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user
```

**Key Patterns**:
- Always use `await session.execute(select(Model))` for queries
- Use `.scalars().all()` to get all rows from a query
- Use `.scalar()` to get a single row
- Use `await session.commit()` after adding/updating
- Use `await session.refresh(obj)` to refresh after commit
- Always await database operations

**CRUD Operations** (in `app/crud.py`):
- Generic CRUD functions for common operations
- All CRUD functions expect `session: AsyncSession` parameter
- CRUD functions should be async when they do database operations
- Example CRUD pattern:
  ```python
  async def get_user_by_email(session: AsyncSession, *, email: str) -> User | None:
      statement = select(User).where(User.email == email)
      result = await session.execute(statement)
      return result.scalar_one_or_none()

  async def create_user(session: AsyncSession, *, user_create: UserCreate) -> User:
      user = User.model_validate(user_create)
      session.add(user)
      await session.commit()
      await session.refresh(user)
      return user
  ```

### 5. Request/Response Models

Separate concerns:

```python
# requests/video_request.py
class VideoRequest(BaseModel):
    upload_name: str
    upload_location: str

# responses/add_video_response.py
class AddVideoResponse(BaseModel):
    video_id: str
    upload_name: str
    upload_location: str
    status: str
```

### 6. Service Layer (Optional)

Business logic separated into services:

```python
# app/services/media_service.py
class MediaService:
    async def add_new_video(self, session: SessionDep, request: VideoRequest):
        # Business logic here
        # Use repository if complex data access
        pass

    def get_media(self, request: VideoRequest):
        # Or direct CRUD
        pass
```

### 7. Dependencies Injection

Centralized in `app/api/deps.py`:

```python
# Session dependency
async def get_db_session() -> AsyncSession:
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session

# Current authenticated user
async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    payload = security.decode_access_token(token)
    user = crud.get_user_by_id(session, payload["sub"])
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
```

## Configuration

Environment variables in `.env`:

```
DB_SERVER=localhost
DB_PORT=3306
DB_USER=user
DB_PASSWORD=password
DB_DB=database
ENVIRONMENT=local
FRONTEND_HOST=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

Configuration in `app/config.py` using pydantic-settings.

## Database Migrations

**Workflow**:
1. Modify models in `app/models.py`
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `app/alembic/versions/`
4. Run `alembic upgrade head` to apply
5. Commit migration file

**Migration locations**:
- `e2412789c190_initialize_models.py` - Initial schema
- `f573b6cd8e2e_create_initial_tables.py` - More tables
- `fc2afb5a5fea_generate_for_church_work.py` - Church service tables
- `f9e7782c04b6_create_init_migration_with_media_.py` - Media tables
- Recent migrations - cascade deletes, nullable fields, etc.

## Testing

**Structure**:
```
tests/
├── conftest.py              # Fixtures
├── api/
│   └── routes/
│       ├── test_login.py
│       ├── test_private.py
│       └── test_users.py
├── crud/
│   └── test_user.py
└── utils/
    └── item.py
```

**Run tests**:
```bash
# Local
poetry run pytest

# Docker
docker-compose test
```

## Scripts

- `scripts/prestart.sh` - Setup before starting app
- `scripts/test.sh` - Run tests
- `scripts/format.sh` - Format code (black, isort)
- `scripts/lint.sh` - Lint code (ruff, flake8)

## Development Setup

### Local (Mac/Linux)
```bash
python3 setup_poetry.py
poetry env activate
poetry install
poetry run fastapi dev main.py
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f be
```

### SSL Certificates
Required in production: `../../infrastructure/certs/cert.pem` and `key.pem`

## Common Gotchas

### Async/Await Sessions
- Always use async functions in route handlers
- Use `session.exec(select(Model))` not `session.query(Model)`
- Sessions must be awaited when getting results

### UUID Fields
- New models use UUID strings (`new_id: str = Field(default_factory=uuid.uuid4)`)
- ID fields use integers for backward compatibility
- Ensure both ID types exist in relations

### Password Hashing
- Use `security.get_password_hash()` for hashing
- Compare with `security.verify_password()`
- Never store plain text passwords

### Error Handling
- Use `HTTPException` with descriptive messages
- Include status codes (400, 401, 403, 404)
- Superuser checks before allowing access

### Email Templates
- Use MJML format in `app/email-templates/src/`
- Build to HTML in `app/email-templates/build/`
- Email functions in `app/utils.py`

## Recent Development

**Branch**: `main`

Migrations applied:
- `e2412789c190_initialize_models.py` — Initial schema
- `f573b6cd8e2e_create_initial_tables.py` — Core tables
- `fc2afb5a5fea_generate_for_church_work.py` — Church service tables
- `f9e7782c04b6_create_init_migration_with_media_.py` — Media tables
- Various migrations — cascade deletes, nullable fields, feature flags, integrations, payments, client credentials, user scopes, assignments

## Next Steps for New Agents

1. Read this file first
2. Check `app/models.py` for database structure
3. Review `app/api/deps.py` for dependencies
4. Look at existing routes (`login.py`, `users.py`) for patterns
5. Run migrations: `alembic upgrade head`
6. Check `.env` file for configuration
7. Use pytest to understand expected behavior
