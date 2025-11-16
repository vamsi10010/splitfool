# Splitfool

Disclaimer: vibe-coded for personal use

## Features

- **User Management**: Add, modify, and delete participants with validation
- **Bill Entry**: Create bills with multiple items and custom split fractions
- **Balance Tracking**: View net outstanding balances between users
- **Settlement**: Clear all balances with a single action and timestamp tracking
- **Bill History**: Review past transactions with full itemized details
- **Keyboard-First**: Complete keyboard navigation with intuitive shortcuts
- **Persistent Storage**: All data saved locally in SQLite database

## Requirements

- Python 3.11 or higher
- uv (Python package manager) - [Installation guide](https://github.com/astral-sh/uv)
- Terminal with ANSI color support (Linux, macOS, Windows Terminal)
- Minimum terminal size: 40x10 (recommended: 80x24 or larger)

## Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd splitfool

# Install dependencies using uv
uv sync

# Run the application
uv run splitfool
```

### Alternative Installation

```bash
# Install from source
uv pip install -e .

# Run directly
splitfool
```

### Custom Database Location

```bash
# Specify custom database path
uv run splitfool --db-path /path/to/custom/splitfool.db
```

## Usage Guide

### Getting Started

1. **Launch the application**: Run `uv run splitfool`
2. **Add users**: Press `Ctrl+N` or navigate to "Manage Users"
3. **Create a bill**: Press `Ctrl+B` to start entering a new bill
4. **View balances**: Press `Ctrl+V` to see who owes what
5. **Settle up**: From the balance view, select "Settle All Balances"
6. **Review history**: Press `Ctrl+H` to see past bills

### User Management

**Adding a User:**
1. From home screen, press `Ctrl+N` or select "Manage Users"
2. Click "Add User" or press `Ctrl+N` again
3. Enter a unique name (1-100 characters)
4. Press Enter to save

**Editing a User:**
1. Navigate to user list
2. Select user and press Enter or click Edit
3. Modify name and press Enter to save

**Deleting a User:**
1. Navigate to user list
2. Select user and press Delete or click Delete button
3. Confirm deletion (blocked if user has outstanding balances)

### Bill Entry

**Creating a Bill:**
1. Press `Ctrl+B` from any screen
2. Enter bill description (optional, max 500 characters)
3. Select who paid the bill (payer)
4. Add tax/tip amount (optional, defaults to $0.00)

**Adding Items:**
1. Click "Add Item" or use keyboard shortcut
2. Enter item description (required)
3. Enter item cost (must be positive)
4. Assign users to split this item
5. Specify fractions for each user (default: equal split)
   - Fractions must sum to 1.0 (e.g., 0.5 + 0.5 or 0.33 + 0.33 + 0.34)
6. Repeat for all items

**Finalizing a Bill:**
1. Review the preview showing each user's owed amount
2. Verify calculations are correct
3. Click "Finalize" or press shortcut to save
4. Bill is saved and balances are updated

**Example Bill:**
```
Description: "Dinner at Restaurant"
Payer: Alice
Tax: $12.00

Items:
- Pizza ($30.00) → Split equally between Alice, Bob, Carol
- Salad ($15.00) → Split equally between Bob, Carol
- Drinks ($12.00) → Only Alice (fraction: 1.0)

Calculations:
- Pizza per person: $10.00
- Salad per person: $7.50
- Tax distribution (proportional to item costs):
  - Alice: $12.00 × (10.00 + 12.00) / 57.00 = $4.63
  - Bob: $12.00 × (10.00 + 7.50) / 57.00 = $3.68
  - Carol: $12.00 × (10.00 + 7.50) / 57.00 = $3.68

Final Amounts Owed to Alice:
- Bob: $10.00 + $7.50 + $3.68 = $21.18
- Carol: $10.00 + $7.50 + $3.68 = $21.18
```

### Balance Viewing

**Understanding Balances:**
- Balances show net amounts between users
- Mutual debts are automatically netted out
- Format: "Bob owes Alice: $21.18"
- Only non-zero balances are displayed

**Settling Balances:**
1. Navigate to Balance View (`Ctrl+V`)
2. Review all outstanding balances
3. Click "Settle All Balances"
4. Confirm the settlement
5. All balances reset to $0.00
6. Settlement timestamp is recorded
7. Historical bills remain accessible

**Important:** Settlement is all-or-nothing. You cannot settle individual balances.

### Bill History

**Viewing History:**
1. Press `Ctrl+H` to view bill history
2. Bills are listed chronologically (most recent first)
3. Select a bill to view full details

**Bill Details Include:**
- Description and timestamp
- Who paid the bill
- All items with costs
- User assignments and fractions
- Tax amount and distribution
- Calculated amounts each user owes

### Keyboard Shortcuts

**Global Shortcuts (work on any screen):**
- `F1` or `?`: Show help
- `Esc`: Go back / Cancel
- `Tab`: Navigate between fields/buttons
- `Arrow Keys`: Navigate lists and menus
- `Enter`: Select / Confirm
- `Ctrl+Q`: Quit application

**Screen-Specific Shortcuts:**
- `Ctrl+N`: New user (from home or user management)
- `Ctrl+B`: New bill (from home screen)
- `Ctrl+V`: View balances
- `Ctrl+H`: View bill history
- `Delete`: Delete selected item/user

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=splitfool --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_services.py

# Run tests matching pattern
uv run pytest -k "test_user"

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code Quality

```bash
# Type checking with mypy (strict mode)
uv run mypy splitfool

# Linting with ruff
uv run ruff check splitfool

# Auto-fix linting issues
uv run ruff check --fix splitfool

# Format code
uv run ruff format splitfool
```

### Project Structure

```
splitfool/
├── __init__.py           # Package initialization
├── __main__.py          # Entry point (CLI argument parsing)
├── config.py            # Configuration (database path, defaults)
├── models/              # Data models (User, Bill, Item, etc.)
├── db/                  # Database layer
│   ├── connection.py    # Connection management
│   ├── schema.py        # SQL schema definitions
│   └── repositories/    # Data access layer (UserRepository, etc.)
├── services/            # Business logic layer
│   ├── user_service.py
│   ├── bill_service.py
│   ├── balance_service.py
│   └── validation.py
├── ui/                  # Textual TUI components
│   ├── app.py          # Main application
│   ├── screens/        # Screen definitions
│   └── widgets/        # Reusable widgets
└── utils/              # Utility functions
    ├── currency.py     # Decimal currency handling
    └── errors.py       # Custom exception classes

tests/
├── unit/               # Unit tests (models, services, utilities)
├── integration/        # Integration tests (database, workflows)
└── fixtures/           # Test fixtures and helpers
```

## Architecture

### Design Principles

- **Immutable Data Models**: Uses `@dataclass(frozen=True)` for all entities
- **Repository Pattern**: Separates data access from business logic
- **Service Layer**: Encapsulates business rules and validation
- **Type Safety**: Comprehensive type hints with mypy strict mode
- **Currency Precision**: Uses `Decimal` type for all monetary calculations
- **Parameterized Queries**: SQL injection prevention via prepared statements

### Data Persistence

All data is stored in a local SQLite database (`splitfool.db` by default):
- **Users**: Participant information with unique names
- **Bills**: Container for expenses with payer and timestamp
- **Items**: Individual line items within bills
- **Assignments**: User-to-item mappings with fractions
- **Settlements**: Timestamps of balance clearing events

Database schema includes proper foreign keys, indexes, and constraints for data integrity.

### Balance Calculation Algorithm

1. Query all bills since last settlement timestamp
2. For each bill, calculate each user's share:
   - Sum assigned item costs × fractions
   - Add proportional tax based on item cost ratios
3. Aggregate debts: for each bill, non-payers owe payer their share
4. Net mutual debts: if Alice owes Bob $50 and Bob owes Alice $30, simplify to Alice owes Bob $20
5. Return only positive balances (amounts > $0.01)

## Troubleshooting

### Database Issues

**Corrupt Database:**
```bash
# Backup current database
cp splitfool.db splitfool.db.backup

# Remove corrupt database (creates new one on next launch)
rm splitfool.db

# Or specify fresh database location
uv run splitfool --db-path ~/splitfool-new.db
```

**Permission Errors:**
Ensure the directory containing `splitfool.db` has write permissions.

### Display Issues

**Colors Not Showing:**
Ensure your terminal supports ANSI colors. Try a modern terminal emulator (Windows Terminal, iTerm2, Alacritty).

**Layout Problems:**
Resize terminal to at least 80x24. The app works at 40x10 but may require scrolling.

### Performance Issues

**Slow Balance Calculation:**
Expected time: <5 seconds for 100 users, 1000 bills. If slower, consider:
- Reducing bill history (settle balances to reset calculation baseline)
- Running on SSD storage
- Checking for database corruption

## Contributing

We follow strict code quality standards (see `.specify/memory/constitution.md`):
- 80%+ test coverage (95%+ for business logic)
- Zero type errors (mypy --strict)
- Zero linting errors (ruff)
- Comprehensive docstrings
- Immutable data structures

## License

MIT License

## Project Status

**Version 0.1.0** - Production Ready

**Tested With:**
- Python 3.11, 3.12
- Textual 0.47.0+
- Linux, macOS, Windows Terminal

**Known Limitations:**
- Single-user only (no concurrent access)
- No network/cloud sync capabilities
- Settlement is all-or-nothing (cannot settle individual balances)

For feature requests and bug reports, please open an issue on the repository.
