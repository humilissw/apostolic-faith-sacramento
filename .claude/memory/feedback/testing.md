---
name: testing
description: Testing guidelines and patterns for this codebase
type: feedback
---

# Testing Practices

## Rules

**Integration tests must use real database connections, not mocks.**

**Why**: Database migrations and actual queries are tested by integration tests. Mocks can pass while migrations fail.

**How to apply**: In `tests/`, always use `conftest.py` fixtures that create real database tables:
```python
@pytest.fixture
def db_session(engine, session_maker):
    """Create a real async session with a fresh database."""
    async with session_maker() as session:
        yield session
```

**Test routes with proper authentication.**

**Why**: Routes with `CurrentUser` dependency need valid tokens.

**How to apply**:
- Use `get_test_token()` fixture from conftest
- Include token in request headers: `Authorization: Bearer <token>`
- Test both superuser and regular user scenarios

**Follow pytest fixture patterns from conftest.py.**

**Why**: Shared fixtures keep tests consistent and reduce duplication.

**How to apply**:
- Use `db_session` for database operations
- Use `client` for FastAPI test client
- Use `get_test_token()` for authentication
- Create test data in `conftest.py` instead of each test

**Run tests before committing.**

**Why**: Catches regressions early.

**How to apply**: Always run `poetry run pytest` or `docker-compose test` before committing

## What to Avoid

- **Never mock database sessions** - Use real database with test fixtures
- **Never skip authentication in auth-related tests** - Always provide valid tokens
- **Never write slow integration tests** - Keep test data minimal
- **Never assume database state** - Always use fresh fixtures

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── api/
│   └── routes/
│       ├── test_login.py    # Auth tests
│       ├── test_private.py  # Local-only routes
│       └── test_users.py    # User CRUD
├── crud/
│   └── test_user.py         # CRUD function tests
└── scripts/
    └── test_*.py            # Script tests
```
