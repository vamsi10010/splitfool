# Splitfool

A Terminal User Interface (TUI) application for splitting bills among multiple users.

## Features

- **User Management**: Add, modify, and delete participants
- **Bill Entry**: Create bills with multiple items and custom split fractions
- **Balance Tracking**: View outstanding balances between users
- **Settlement**: Clear all balances with a single action
- **Bill History**: Review past transactions with full details

## Requirements

- Python 3.11 or higher
- uv (Python package manager)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd splitfool

# Install dependencies
uv sync

# Run the application
uv run splitfool
```

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=splitfool --cov-report=html

# Type checking
uv run mypy splitfool

# Linting and formatting
uv run ruff check splitfool
uv run ruff format splitfool
```

## Usage

Launch the application:

```bash
uv run splitfool
```

Navigate using keyboard shortcuts:
- `Ctrl+N`: New user
- `Ctrl+B`: New bill
- `Ctrl+V`: View balances
- `Ctrl+H`: View history
- `F1` or `?`: Help
- `Esc`: Go back

## License

MIT License

## Project Status

Version 0.1.0 - Initial Development
