# MediaRepository Test Suite

This directory contains comprehensive tests for the `MediaRepository` class using mocks.

## Purpose

These tests demonstrate the benefits of the repository pattern by testing database logic in isolation without requiring a real database connection or environment configuration.

## Test Files

1. **standalone_test_media_repo.py** - Complete test suite with 16 tests covering:
   - Basic CRUD operations
   - Pagination
   - Edge cases (unicode, emojis, long names, etc.)
   - Integration scenarios

2. **test_media_repo.py** - Comprehensive tests with detailed scenarios

3. **test_media_repo_simple.py** - Simpler test cases for quick verification

## Running the Tests

### From the repository root:

```bash
cd /Users/cloud/code/apostolic-faith-sacramento/src/be
poetry run pytest tests/repositories/standalone_test_media_repo.py -v
```

### Run all repository tests:

```bash
poetry run pytest tests/repositories/ -v
```

### Run with coverage:

```bash
poetry run pytest tests/repositories/standalone_test_media_repo.py --cov=app.repositories.media_repo --cov-report=html
```

## Test Coverage

The test suite covers:

### CRUD Operations
- ✅ Create media entries
- ✅ Retrieve media by ID
- ✅ Retrieve all media with pagination
- ✅ Update media entries
- ✅ Delete media entries

### Edge Cases
- ✅ Very long names (200 characters)
- ✅ Unicode characters (Café, naïve, etc.)
- ✅ Emoji in names (🎬 Movie 🎬)
- ✅ Empty update data
- ✅ Non-existent records
- ✅ Limit of 0
- ✅ Negative skip values

### Integration Scenarios
- ✅ Complete CRUD workflow
- ✅ Multiple operations in sequence
- ✅ Session management verification

## Mocking Strategy

The tests use `unittest.mock` to simulate database operations:

```python
# Mock AsyncSession
mock_session = MagicMock(spec=AsyncSession)

# Mock execute to return expected results
mock_result = MagicMock()
mock_result.scalar_one_or_none.return_value = media_object
mock_session.execute = AsyncMock(return_value=mock_result)
```

## Benefits

1. **Fast Execution**: Tests run without database connections
2. **Isolated Testing**: Each test validates a single method
3. **No Environment Setup**: No need for database configuration
4. **Clear Assertions**: Easy to understand what each test verifies
5. **Edge Case Coverage**: Tests unusual scenarios that might fail in production

## Example Test

```python
@pytest.mark.asyncio
async def test_create_media(self, mock_async_session: AsyncSession) -> None:
    """Test creating a new media entry."""
    repository = MediaRepository(session=mock_async_session)
    media_in = MediaCreate(name="Test Media")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_execute = AsyncMock(return_value=mock_result)
    mock_async_session.execute = mock_execute

    media = await repository.create(media_in=media_in)

    assert media is not None
    assert media.name == "Test Media"
    assert mock_async_session.add.called
```

## Writing New Tests

To add new tests to this suite:

1. Create a new test class inheriting from `TestMediaRepository[OperationName]`
2. Use the `@pytest.mark.asyncio` decorator for async tests
3. Use the `mock_async_session` fixture provided
4. Follow the naming convention: `test_[operation]_[scenario]`
5. Add clear assertions and documentation

## See Also

- [Repository Pattern Documentation](../../../REFACTORING_SUMMARY.md)
- [MediaRepository Source](../../app/repositories/media_repo.py)
- [Media Tests](../routes/test_media.py) - API-level tests with database
