---
name: coding-conventions
description: Preferred coding patterns and what to avoid in this codebase
type: feedback
---

# Coding Conventions

## Rules

**Always use async/await for database operations.**

**Why**: The entire codebase uses async sessions with SQLAlchemy/SQLModel. Blocking operations will cause database deadlocks and performance issues.

**How to apply**: Every database operation must use `await`:
- `await session.execute(select(Model))` instead of `session.exec()`
- `await session.commit()` instead of `session.commit()`
- `await session.refresh(obj)` instead of `session.refresh(obj)`

**Use type hints for all function parameters and return values.**

**Why**: The codebase uses Python 3.13+ and relies on type hints for IDE support and static analysis.

**How to apply**: Always include type hints:
```python
async def read_items(session: AsyncSession, current_user: CurrentUser, skip: int = 0) -> List[Item]:
    ...
```

**Follow the existing route structure patterns.**

**Why**: The codebase follows established patterns for API routes. Consistency makes the codebase easier to navigate.

**How to apply**:
- Import from `app.api.deps` for dependencies
- Use `APIRouter` with prefix and tags
- Include health check endpoints for all routes
- Use `CurrentUser` dependency for authentication
- Check permissions using `current_user.is_superuser`

**Use pydantic models for request/response validation.**

**Why**: Pydantic models handle validation and serialization automatically.

**How to apply**:
- Create separate models in `app/requests/` for input
- Create separate models in `app/responses/` for output
- Exclude internal fields (like `hashed_password`) from public models

**Separate concerns with service layer when business logic is complex.**

**Why**: Keeps routes clean and business logic reusable.

**How to apply**:
- Create service classes in `app/services/`
- Pass AsyncSession to service methods
- Let routes call service methods

**Always handle exceptions properly.**

**Why**: Clear error messages help debugging and user experience.

**How to apply**:
- Use `HTTPException` with descriptive messages
- Include appropriate status codes (400, 401, 403, 404)
- Never expose raw database errors to users

## What to Avoid

- **Never block async operations** - Don't use `await` inside non-async functions or vice versa
- **Never skip type hints** - Even for simple functions
- **Never hardcode database credentials** - Always use environment variables
- **Never commit secrets** - Never commit `.env` or `.env.prod` files
- **Never skip permission checks** - Always verify `current_user.is_superuser` or `owner_id` matches
- **Never use synchronous database drivers** - Use asyncmy, not mysql-connector-python for async operations
