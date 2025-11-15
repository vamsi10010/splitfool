# Implementation Plan: Splitfool TUI Bill-Splitting Application

**Branch**: `001-tui-bill-splitter` | **Date**: 2025-11-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-tui-bill-splitter/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Splitfool is a terminal user interface (TUI) application for splitting bills among multiple users. The application will be built using Python with the Textual framework for the TUI, SQLite for data persistence, and uv for project management. Users can manage participants, enter bills with itemized costs and custom split fractions, view outstanding balances, and settle all balances with a single action. All data persists locally in an SQLite database for cross-session availability.

## Technical Context

**Language/Version**: Python 3.11+ (resolved: performance and syntax benefits over 3.10)  
**Primary Dependencies**: 
  - Textual (TUI framework from https://github.com/Textualize/textual)
  - sqlite3 (built-in Python standard library)
  - decimal.Decimal (standard library for currency precision)
  - pytest + pytest-cov (testing framework)
  - mypy (type checking with --strict mode)
  - ruff (linting and formatting)
**Database Access**: Raw sqlite3 with Repository Pattern (resolved: simplicity over ORM for this use case)  
**Storage**: SQLite database (local file)  
**Testing**: pytest + pytest-cov + Textual pilot mode (70% unit, 20% integration, 10% TUI)  
**Target Platform**: Cross-platform terminals (Linux, macOS, Windows with ANSI support)  
**Project Type**: Single project (standalone TUI application)  
**Performance Goals**: 
  - Application startup: <2 seconds (SC-004)
  - UI responsiveness: <100ms render time (SC-005)
  - Balance view: <5 seconds from any screen (SC-003)
**Constraints**: 
  - Must handle 100+ users, 1000+ bills, 10k+ items (SC-008)
  - Memory usage: reasonable for local desktop application
  - Must work in terminals 40x10 to 200x50 (FR-040)
  - Currency precision: ±$0.01 rounding tolerance (SC-010)
**Scale/Scope**: 
  - Personal/small group use (up to 100 users per assumption)
  - 6 main screens (home, user management, bill entry, balance view, history, help)
  - Estimated ~2000-3000 LOC for core application
  - Single-user local access (no networking/multi-user)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality (Section I)
- ✅ **1.2 Type Safety**: All Python code will use comprehensive type hints
- ✅ **1.3 Documentation**: Module and function docstrings following Google style
- ✅ **1.4 Error Handling**: Custom exception classes for domain errors, proper error messages (FR-047)
- ✅ **1.5 Dependency Management**: uv for management, pyproject.toml for declarations
- ✅ **1.8 Security**: No credentials in code, parameterized DB queries, input validation (FR-048-051)
- ✅ **1.9 Immutability**: Use frozen dataclasses for data models

### Testing Standards (Section II)
- ✅ **2.1 Coverage**: Target 80%+ coverage, 95%+ for business logic (balance calculations)
- ✅ **2.2 Structure**: Mirror source structure, descriptive test names
- ✅ **2.4 Test Types**: Unit tests for calculations, integration tests for DB, TUI testing approach TBD

### User Experience (Section III)
- ✅ **3.1 Error Messages**: Clear, actionable error messages with error codes (FR-047)
- ✅ **3.3 CLI Standards**: Keyboard shortcuts (FR-041), help section (FR-042-043), exit codes
- ✅ **3.4 Accessibility**: Keyboard-only navigation (SC-006), terminal size adaptation (FR-040)
- ✅ **3.6 Terminology**: Consistent terms (User, Bill, Item, Balance, Settlement) from spec

### Performance (Section IV)
- ✅ **4.1 Response Times**: <2s startup, <100ms UI, <5s balance view (SC-004, SC-005, SC-003)
- ✅ **4.4 Database**: Proper indexing for foreign keys, pagination for large lists
- ⚠️ **4.3 Scalability**: Single-user local app - horizontal scalability N/A (justified by use case)

### MCP Server (Section V)
- ⚠️ **Not Applicable**: This is a standalone TUI application, not an MCP server implementation

### Violations/Justifications
**None requiring complexity tracking** - This is a greenfield single-project TUI application that aligns with all applicable constitution principles. MCP and horizontal scalability sections are not applicable to the local single-user use case.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
splitfool/                    # Main application package
├── __init__.py
├── __main__.py              # Entry point for `python -m splitfool`
├── models/                  # Data models (User, Bill, Item, etc.)
│   ├── __init__.py
│   ├── user.py
│   ├── bill.py
│   ├── item.py
│   ├── assignment.py
│   ├── balance.py
│   └── settlement.py
├── db/                      # Database layer
│   ├── __init__.py
│   ├── connection.py        # SQLite connection management
│   ├── schema.py            # Database schema definitions
│   ├── migrations.py        # Schema migration handling
│   └── repositories/        # Data access layer
│       ├── __init__.py
│       ├── user_repository.py
│       ├── bill_repository.py
│       └── balance_repository.py
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── user_service.py      # User CRUD operations
│   ├── bill_service.py      # Bill creation and calculations
│   ├── balance_service.py   # Balance calculation and settlement
│   └── validation.py        # Input validation logic
├── ui/                      # Textual TUI components
│   ├── __init__.py
│   ├── app.py               # Main Textual app class
│   ├── screens/             # TUI screens
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── user_management.py
│   │   ├── bill_entry.py
│   │   ├── balance_view.py
│   │   ├── history.py
│   │   └── help.py
│   └── widgets/             # Reusable UI components
│       ├── __init__.py
│       ├── user_list.py
│       ├── bill_form.py
│       └── balance_table.py
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── currency.py          # Decimal/currency handling
│   └── errors.py            # Custom exception classes
└── config.py                # Configuration management

tests/
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_validation.py
│   └── test_currency.py
├── integration/             # Integration tests
│   ├── test_repositories.py
│   ├── test_bill_workflow.py
│   └── test_balance_calculation.py
└── fixtures/                # Test data and fixtures
    ├── __init__.py
    └── sample_data.py

pyproject.toml               # uv/pip project configuration
README.md                    # Project documentation
.gitignore
```

**Structure Decision**: Single project structure selected. This is a standalone TUI application with clear separation of concerns:
- **models/**: Immutable data classes representing domain entities
- **db/**: Database access layer with repository pattern for testability
- **services/**: Business logic isolated from UI and data layers
- **ui/**: Textual-specific UI code organized by screens and reusable widgets
- **utils/**: Cross-cutting concerns (currency math, custom errors)

This structure supports the constitution requirements for modularity (1.6), testability (2.2), and separation of concerns (1.10).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations requiring justification.** All architectural decisions align with constitution principles and are appropriate for the application's scope and requirements.

---

## Phase Completion Status

### ✅ Phase 0: Research & Clarification (COMPLETE)
**Output**: `research.md`

All NEEDS CLARIFICATION items resolved:
- ✅ Python version: 3.11+ selected
- ✅ Database access: Raw sqlite3 with Repository Pattern
- ✅ Currency handling: decimal.Decimal from standard library
- ✅ Testing strategy: pytest + pytest-cov + Textual pilot mode
- ✅ TUI architecture: Textual screens + widgets + services pattern
- ✅ Error handling: Custom exceptions + manual validation

**Key Decisions Documented**:
- Technology choices with rationale
- Alternatives considered and rejected
- Constitution alignment verification
- Implementation patterns defined

### ✅ Phase 1: Design & Contracts (COMPLETE)
**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`, agent context updated

**Data Model** (6 entities defined):
- ✅ User: Participant management with validation
- ✅ Bill: Expense container with payer and tax
- ✅ Item: Line items with costs
- ✅ Assignment: Item-to-user mappings with fractions
- ✅ Balance: Derived entity for debt tracking
- ✅ Settlement: Bulk balance clearing records

**Database Schema**:
- ✅ Complete SQLite schema with proper indexes
- ✅ Foreign key constraints defined
- ✅ Validation rules at DB level
- ✅ Migration strategy defined

**Service Contracts** (3 interfaces):
- ✅ `user_service.py`: User CRUD operations (FR-001 to FR-007)
- ✅ `bill_service.py`: Bill creation and calculations (FR-008 to FR-033)
- ✅ `balance_service.py`: Balance calculation and settlement (FR-024 to FR-029)

**Documentation**:
- ✅ `quickstart.md`: Complete development setup guide
- ✅ `.github/agents/copilot-instructions.md`: Agent context with tech stack

**Constitution Re-Check**: ✅ All principles satisfied, no violations

### 🔲 Phase 2: Implementation Tasks (PENDING)
**Next Command**: `/speckit.tasks`

This will generate `tasks.md` with:
- Atomic, testable implementation tasks
- Priority ordering by user story
- Dependency tracking between tasks
- Acceptance criteria per task

---

## Next Steps

The planning phase is complete. To proceed with implementation:

1. **Run** `/speckit.tasks` to generate the task breakdown
2. **Review** the generated task list for completeness
3. **Begin** implementation following the task order
4. **Refer** to:
   - `research.md` for technology decisions
   - `data-model.md` for entity definitions
   - `contracts/` for service interfaces
   - `quickstart.md` for development workflow
   - Constitution at `.specify/memory/constitution.md` for quality standards

**Estimated Implementation Time**: 2-3 weeks for full feature (based on ~2000-3000 LOC estimate)

**Current Branch**: `001-tui-bill-splitter`  
**Status**: Ready for Phase 2 (tasks generation)
