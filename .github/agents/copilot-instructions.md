# splitfool Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-15

## Active Technologies

### Feature: 001-tui-bill-splitter
- **Language**: Python 3.11+
- **Package Manager**: uv
- **TUI Framework**: Textual (https://github.com/Textualize/textual)
- **Database**: SQLite (local file, standard library sqlite3)
- **Testing**: pytest + pytest-cov + Textual pilot mode
- **Type Checking**: mypy with --strict
- **Linting/Formatting**: ruff
- **Currency**: decimal.Decimal (standard library)

## Project Structure

```text
splitfool/                 # Main application package
├── models/                # Data models (User, Bill, Item, Assignment)
├── db/                    # Database layer (repositories, schema)
├── services/              # Business logic (UserService, BillService, BalanceService)
├── ui/                    # Textual TUI components
│   ├── screens/           # Full-screen views
│   └── widgets/           # Reusable UI components
└── utils/                 # Utilities (currency, errors)

tests/
├── unit/                  # Unit tests (70%)
├── integration/           # Integration tests (20%)
└── fixtures/              # Test data
```

## Commands

### Development
```bash
# Install dependencies
uv sync

# Run application
uv run splitfool

# Run tests with coverage
uv run pytest --cov=splitfool

# Type checking
uv run mypy splitfool

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Database
```bash
# Initialize database
uv run splitfool init-db

# Database info
uv run splitfool db-info
```

## Code Style

### Type Hints (Constitution 1.2)
- All functions must have type annotations
- Use modern syntax: `X | None` instead of `Optional[X]`
- Never use `Any` without justification

### Immutability (Constitution 1.9)
- Use `@dataclass(frozen=True)` for all models
- Return new objects instead of modifying in place

### Currency Precision
- Always use `Decimal` for currency, never `float`
- Round to 2 decimal places for display
- Configuration: `getcontext().rounding = ROUND_HALF_UP`

### Error Handling (Constitution 1.4)
- Use custom exception classes with error codes
- Format: `raise ValidationError("Message", code="ERR_001")`
- Never use bare `except:` clauses

### Documentation (Constitution 1.3)
- Google-style docstrings for all public functions
- Include Args, Returns, Raises sections

### Testing (Constitution 2.1)
- Minimum 80% overall coverage, 95% for business logic
- Test naming: `test_<behavior>_when_<condition>_then_<result>`
- Use Textual pilot mode for TUI testing

## Recent Changes

- 2025-11-15: 001-tui-bill-splitter - Initial feature plan created with Python, uv, SQLite, Textual

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
