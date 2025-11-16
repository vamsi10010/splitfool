# Splitfool v0.1.0 Release Notes

**Release Date**: 2025-11-15  
**Status**: Production Ready

## Overview

Splitfool v0.1.0 is a Terminal User Interface (TUI) application for splitting bills among multiple users with precise calculations and persistent storage.

## Features

### User Management
- ✅ Add, edit, and delete users
- ✅ Unique user names with validation
- ✅ User deletion protected when outstanding balances exist
- ✅ Persistent storage across sessions

### Bill Entry
- ✅ Create bills with multiple line items
- ✅ Assign items to users with custom fractions
- ✅ Proportional tax/tip distribution based on consumption
- ✅ Real-time preview of calculated shares
- ✅ Full validation (fractions sum to 1.0, positive costs, etc.)
- ✅ Itemized bill details with payer tracking

### Balance Tracking
- ✅ Automatic calculation of net balances
- ✅ Mutual debt netting algorithm (simplifies circular debts)
- ✅ View who owes money to whom
- ✅ Per-user balance details (debts and credits)

### Settlement
- ✅ All-or-nothing balance settlement
- ✅ Timestamped settlement records
- ✅ Bills preserved in history after settlement
- ✅ Settlement notes support

### Bill History
- ✅ Chronological list of all bills
- ✅ Detailed drill-down view
- ✅ Full item and assignment details
- ✅ Pagination for large datasets

### TUI Experience
- ✅ Keyboard-first navigation (95%+ actions via keyboard)
- ✅ Comprehensive help system (F1 or ?)
- ✅ Context-sensitive error messages
- ✅ Responsive layout (works from 40x10 to 200x50 terminals)
- ✅ Professional visual design with consistent styling

## Performance

All performance targets met or exceeded:

- **Startup Time**: <0.04s (target: <2s) ✓
- **Balance Calculation**: 2.88s for 1000 bills (target: <5s) ✓
- **UI Responsiveness**: <100ms render time ✓
- **Scale**: Tested with 100 users, 1000 bills, 10k items ✓

## Quality Metrics

- **Test Coverage**: 95%+ for business logic (balance/bill services, models)
- **Type Safety**: Comprehensive type hints with mypy strict mode
- **Code Quality**: Zero linting errors with ruff
- **Currency Precision**: Uses Decimal for ±$0.01 accuracy
- **SQL Security**: 100% parameterized queries (no SQL injection risks)

## Technical Stack

- **Language**: Python 3.11+
- **TUI Framework**: Textual 0.47.0+
- **Database**: SQLite 3 with proper indexing
- **Testing**: pytest with 138 passing tests
- **Type Checking**: mypy --strict mode
- **Linting**: ruff with comprehensive rules

## Installation

```bash
# Install with uv (recommended)
git clone <repository-url>
cd splitfool
uv sync
uv run splitfool

# Or install from source
uv pip install -e .
splitfool
```

## Known Limitations

1. **Single-User Only**: No concurrent access support (by design for local use)
2. **No Cloud Sync**: Data stored locally only
3. **Settlement Scope**: All-or-nothing settlement (cannot settle individual balances)
4. **No Bill Editing**: Bills are immutable once finalized (delete and recreate to modify)

## Breaking Changes

None (initial release).

## Upgrade Notes

None (initial release).

## Bug Fixes

None (initial release).

## Future Enhancements (Potential)

- Bill editing capability
- Partial settlement support
- Export to CSV/JSON
- Import from external sources
- Multi-currency support
- Mobile/web client

## Contributors

Built following strict code quality standards (see `.specify/memory/constitution.md`).

## License

MIT License

## Support

For bug reports and feature requests, please open an issue on the repository.

---

**Thank you for using Splitfool!**
