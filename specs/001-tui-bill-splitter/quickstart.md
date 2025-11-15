# Quickstart Guide: Splitfool Development

**Feature**: 001-tui-bill-splitter  
**Date**: 2025-11-15  
**Audience**: Developers setting up the project for the first time

## Prerequisites

- **Python 3.11+**: Check with `python3 --version`
- **uv**: Modern Python package manager ([Installation](https://github.com/astral-sh/uv))
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Git**: For version control
- **Terminal**: ANSI-compatible terminal (most modern terminals)

---

## Project Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd splitfool
```

### 2. Install Dependencies
```bash
# uv will create a virtual environment and install dependencies from pyproject.toml
uv sync

# Activate the virtual environment (if not auto-activated)
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

### 3. Initialize Database
```bash
# Run database initialization (creates splitfool.db)
uv run python -m splitfool init-db

# OR use the CLI command once implemented
uv run splitfool init-db
```

### 4. Verify Installation
```bash
# Run tests to ensure everything is working
uv run pytest

# Try launching the app
uv run python -m splitfool

# OR
uv run splitfool
```

---

## Development Workflow

### Running the Application
```bash
# Standard way
uv run python -m splitfool

# Or use the entry point
uv run splitfool

# With specific database file
uv run splitfool --db-path ./my-bills.db
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=splitfool --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_user_service.py

# Run tests matching a pattern
uv run pytest -k "test_balance"

# Run with verbose output
uv run pytest -v
```

### Code Quality Checks
```bash
# Type checking with mypy
uv run mypy splitfool

# Code formatting with ruff
uv run ruff format splitfool tests

# Linting with ruff
uv run ruff check splitfool tests

# Auto-fix linting issues
uv run ruff check --fix splitfool tests
```

### Database Management
```bash
# Create fresh database
uv run splitfool init-db

# Create database at specific location
uv run splitfool init-db --path ./data/bills.db

# Check database schema version
uv run splitfool db-info

# Reset database (delete all data)
uv run splitfool reset-db --confirm
```

---

## Project Structure Quick Reference

```
splitfool/
├── splitfool/              # Main application package
│   ├── models/             # Data models (User, Bill, etc.)
│   ├── db/                 # Database layer (connections, repositories)
│   ├── services/           # Business logic (UserService, BillService, etc.)
│   ├── ui/                 # Textual TUI components
│   │   ├── screens/        # Full-screen views
│   │   └── widgets/        # Reusable UI components
│   ├── utils/              # Utilities (currency, errors)
│   └── config.py           # Configuration
├── tests/
│   ├── unit/               # Unit tests (70% of tests)
│   ├── integration/        # Integration tests (20%)
│   └── fixtures/           # Test data
├── specs/                  # Feature specifications and plans
├── pyproject.toml          # Project config and dependencies
└── README.md
```

---

## Key Commands Reference

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` |
| Run app | `uv run splitfool` |
| Run tests | `uv run pytest` |
| Run with coverage | `uv run pytest --cov=splitfool` |
| Type check | `uv run mypy splitfool` |
| Format code | `uv run ruff format .` |
| Lint code | `uv run ruff check .` |
| Initialize DB | `uv run splitfool init-db` |

---

## Development Guidelines

### Adding a New Feature

1. **Create branch** from main:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write tests first** (TDD):
   ```python
   # tests/unit/test_my_feature.py
   def test_my_new_feature():
       # Arrange
       service = MyService()
       
       # Act
       result = service.do_something()
       
       # Assert
       assert result == expected
   ```

3. **Implement feature**:
   - Add models if needed (`splitfool/models/`)
   - Add service methods (`splitfool/services/`)
   - Add UI components (`splitfool/ui/`)

4. **Run quality checks**:
   ```bash
   uv run pytest --cov=splitfool
   uv run mypy splitfool
   uv run ruff check splitfool
   ```

5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add my feature"
   git push origin feature/my-feature
   ```

### Code Style

- **Type hints**: All functions must have type annotations
  ```python
  def calculate_split(total: Decimal, count: int) -> Decimal:
      return total / count
  ```

- **Docstrings**: Use Google style for all public functions
  ```python
  def create_user(name: str) -> User:
      """Create a new user.
      
      Args:
          name: User's display name
          
      Returns:
          Created user with assigned ID
          
      Raises:
          ValidationError: If name is invalid
      """
  ```

- **Immutability**: Use `frozen=True` dataclasses
  ```python
  @dataclass(frozen=True)
  class User:
      id: int | None
      name: str
  ```

- **Error handling**: Use custom exceptions with codes
  ```python
  raise ValidationError("Name cannot be empty", code="USER_001")
  ```

### Testing Guidelines

- **Coverage target**: 80% overall, 95% for business logic
- **Test structure**: Arrange-Act-Assert pattern
- **Test names**: `test_<behavior>_when_<condition>_then_<result>`
  ```python
  def test_create_user_when_name_empty_then_raises_validation_error():
      pass
  ```
- **Fixtures**: Use pytest fixtures for common setup
  ```python
  @pytest.fixture
  def db_connection():
      conn = sqlite3.connect(":memory:")
      initialize_schema(conn)
      yield conn
      conn.close()
  ```

---

## Debugging Tips

### Database Inspection
```bash
# Open database with sqlite3 CLI
sqlite3 splitfool.db

# Common queries
SELECT * FROM users;
SELECT * FROM bills ORDER BY created_at DESC LIMIT 10;
SELECT b.*, u.name as payer FROM bills b JOIN users u ON b.payer_id = u.id;
```

### Textual DevTools
```python
# Enable Textual devtools (in development)
# Add to your app run command:
uv run textual run splitfool.ui.app:SplitfoolApp --dev

# This opens a separate console for debugging
```

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'splitfool'`  
**Fix**: Ensure you're in the virtual environment and have run `uv sync`

**Issue**: `Database is locked`  
**Fix**: Close other connections to the database file

**Issue**: `TypeError: can't multiply Decimal by float`  
**Fix**: Always use `Decimal()` for currency, never mix with float

**Issue**: Tests failing with UI errors  
**Fix**: Ensure you're using Textual's pilot mode for TUI tests:
```python
async with app.run_test() as pilot:
    await pilot.press("enter")
```

---

## Useful Resources

- **Python Decimal**: https://docs.python.org/3/library/decimal.html
- **Textual Docs**: https://textual.textualize.io/
- **uv Documentation**: https://github.com/astral-sh/uv
- **pytest Documentation**: https://docs.pytest.org/
- **SQLite Documentation**: https://www.sqlite.org/docs.html

---

## Next Steps

1. ✅ **Setup complete** - You can now run the application
2. 📖 **Read the specs** - Check `specs/001-tui-bill-splitter/spec.md` for requirements
3. 🏗️ **Review architecture** - See `specs/001-tui-bill-splitter/data-model.md`
4. 🔨 **Start coding** - Follow the task list in `specs/001-tui-bill-splitter/tasks.md` (created by `/speckit.tasks`)
5. ✅ **Run tests frequently** - Maintain 80%+ coverage

---

## Getting Help

- **Technical issues**: Check constitution at `.specify/memory/constitution.md`
- **Feature questions**: Refer to `specs/001-tui-bill-splitter/spec.md`
- **Design questions**: See `specs/001-tui-bill-splitter/data-model.md`
- **API contracts**: Check `specs/001-tui-bill-splitter/contracts/`

**Happy coding! 🚀**
