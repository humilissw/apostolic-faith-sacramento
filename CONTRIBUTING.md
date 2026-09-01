# Contributing to Apostolic Faith Sacramento

Thank you for your interest in contributing to the Apostolic Faith Sacramento project!

## Getting Started

1. **Fork and Clone**: Fork the repository and clone it to your local machine
2. **Set Up Development Environment**:
   ```bash
   # Backend
   cd src/be
   python3 setup_poetry.py
   poetry env activate
   poetry install

   # Frontend
   cd ../fe
   bun install
   ```
3. **Read the Documentation**:
   - `CLAUDE.md` - Project overview and quick start
   - `src/be/CLAUDE.md` - Backend specific guide
   - `src/be/AGENTS.md` - Detailed patterns and conventions

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names following this pattern:
- `feature/add-media-upload`
- `bugfix/fix-auth-error`
- `docs/update-readme`

### Making Changes

1. **Check Memory**: Use Claude Code to check memory for relevant information
2. **Follow Conventions**: Adhere to coding conventions in memory and AGENTS.md
3. **Write Tests**: Add tests for new functionality
4. **Run Tests**: Ensure all tests pass
   ```bash
   poetry run pytest
   ```

### Code Quality

- **Format**: Run formatters
  ```bash
  poetry run bash scripts/format.sh
  ```
- **Lint**: Run linters
  ```bash
  poetry run bash scripts/lint.sh
  ```

### Committing Changes

- Write clear, descriptive commit messages
- Follow conventional commits format:
  ```
  feat: add media upload functionality
  fix: resolve async session deadlock
  docs: update AGENTS.md with async patterns
  test: add unit tests for media service
  refactor: separate business logic into services
  ```

### Pull Request

1. Push your changes
2. Open a pull request with a clear description
3. Include:
   - Summary of changes
   - Related issue(s)
   - Screenshots (for UI changes)
   - Test results

## Testing Guidelines

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database operations
- **End-to-End Tests**: Test user flows (if applicable)
- **Always Run Tests**: Before submitting PRs

## Code Review

- Be responsive to review feedback
- Address comments in a timely manner
- Keep commits focused and small
- Explain complex changes

## Questions?

- Check the [CLAUDE.md](./CLAUDE.md) and [AGENTS.md](./src/be/AGENTS.md) files
- Ask in team channels or create an issue
- Use Claude Code with "tell me about this project" for help understanding

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
