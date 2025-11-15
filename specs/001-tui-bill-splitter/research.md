# Research: Splitfool TUI Bill-Splitting Application

**Feature**: 001-tui-bill-splitter  
**Date**: 2025-11-15  
**Status**: Complete

## Overview

This document resolves all "NEEDS CLARIFICATION" items identified in the Technical Context section of the implementation plan and documents key technology decisions.

---

## Research Topics

### 1. Python Version Compatibility with uv

**Question**: What is the minimum Python version that is compatible with uv and suitable for this project?

**Research Findings**:
- **uv** is a modern Python package manager written in Rust that supports Python 3.8+
- **Textual** requires Python 3.8+ (officially supports 3.8, 3.9, 3.10, 3.11, 3.12)
- **Type hints** improvements in Python 3.10+ (PEP 604 union syntax `X | Y`)
- **Pattern matching** in Python 3.10+ could be useful for UI state management
- **Improved error messages** in Python 3.11+

**Decision**: **Python 3.11+**

**Rationale**:
- Python 3.11 is widely available and stable (released October 2022)
- Provides better type hint syntax (`X | None` instead of `Optional[X]`)
- Significant performance improvements over 3.10 (10-60% faster)
- Better error messages aid development
- Still supported by all major platforms and CI systems

**Alternatives Considered**:
- Python 3.8: Too old, missing modern syntax improvements
- Python 3.10: Good choice but 3.11 performance gains are significant
- Python 3.12: Too new, may have compatibility issues with some tools

---

### 2. Database Access Layer (ORM vs Raw SQL)

**Question**: Should we use an ORM (SQLAlchemy), raw SQL with sqlite3, or another approach?

**Research Findings**:
- **SQLAlchemy**: Full-featured ORM, supports migrations (Alembic), type-safe queries
  - Pros: Type safety, migration support, query building, relationship management
  - Cons: Learning curve, added complexity, overkill for simple schema
  - Constitution alignment: Good for maintainability (1.6), may violate simplicity (1.10)

- **Raw sqlite3**: Built-in Python standard library
  - Pros: Zero dependencies, direct control, simple for small schema
  - Cons: Manual SQL, manual migrations, no relationship management, prone to errors
  - Constitution alignment: Simple but poor type safety (1.2), more error-prone (1.4)

- **SQLModel**: Combines Pydantic and SQLAlchemy, modern approach
  - Pros: Type-safe models, simple API, good for FastAPI-style apps
  - Cons: Less mature, primarily designed for web APIs
  - Constitution alignment: Good type safety but may be overkill

**Decision**: **Raw sqlite3 with Repository Pattern**

**Rationale**:
- Simple schema (6 entities: User, Bill, Item, Assignment, Balance, Settlement)
- No complex relationships or migrations expected
- Constitution 1.5: "Prefer standard library solutions when performance is acceptable"
- Repository pattern provides testability without ORM overhead
- Can always upgrade to SQLAlchemy later if complexity grows (YAGNI principle)
- Manual migrations sufficient for single-user local database

**Alternatives Considered**:
- SQLAlchemy: Over-engineered for this use case, violates simplicity principle
- SQLModel: Adds unnecessary dependency for non-web application

**Implementation Approach**:
```python
# Use dataclasses for models, repositories for data access
@dataclass(frozen=True)
class User:
    id: int | None
    name: str
    created_at: datetime

class UserRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
    
    def create(self, user: User) -> User:
        # Parameterized query for safety (Constitution 1.8)
        cursor = self.conn.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            (user.name, user.created_at)
        )
        return user.replace(id=cursor.lastrowid)
```

---

### 3. Currency and Decimal Precision Handling

**Question**: What library/approach should be used for currency calculations to meet ±$0.01 precision requirement?

**Research Findings**:
- **float**: Standard Python float (IEEE 754)
  - Pros: Built-in, fast
  - Cons: Precision errors (0.1 + 0.2 = 0.30000000000000004), unacceptable for currency
  - Constitution violation: Fails accuracy requirement (SC-010)

- **decimal.Decimal**: Python standard library
  - Pros: Arbitrary precision, exact decimal arithmetic, configurable rounding
  - Cons: Slower than float (acceptable for this use case)
  - Constitution alignment: Type safety (1.2), accuracy requirement met

- **money library**: Third-party currency library
  - Pros: Currency-aware, locale support
  - Cons: Adds dependency, overkill for single-currency app
  - Constitution: Violates dependency minimization (1.5)

**Decision**: **Python standard library `decimal.Decimal`**

**Rationale**:
- Exact decimal arithmetic eliminates floating-point errors
- Built-in library, zero dependencies (Constitution 1.5)
- Configurable precision and rounding modes
- Type hints supported: `Decimal` type
- Performance acceptable for local desktop application

**Alternatives Considered**:
- float: Unacceptable due to precision errors
- money library: Unnecessary dependency for single-currency use case

**Implementation Guidelines**:
```python
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Set global precision for currency (2 decimal places)
getcontext().prec = 10  # Sufficient for calculations
getcontext().rounding = ROUND_HALF_UP

def format_currency(amount: Decimal) -> str:
    """Format Decimal as currency string."""
    return f"${amount.quantize(Decimal('0.01'))}"

def parse_currency(value: str) -> Decimal:
    """Parse user input to Decimal."""
    return Decimal(value.replace('$', '').replace(',', ''))
```

---

### 4. Testing Strategy for TUI Application

**Question**: How should we test a Textual TUI application to meet 80%+ coverage requirement?

**Research Findings**:
- **pytest**: Standard Python testing framework
  - Pros: Fixtures, parametrization, extensive plugin ecosystem
  - Cons: None significant
  - Constitution alignment: Industry standard, good documentation (2.2)

- **Textual Testing**: Textual provides built-in testing support
  - Pilot mode: Run app without rendering for testing
  - Snapshot testing: Compare UI output
  - Component testing: Test widgets in isolation

- **Coverage Tools**: pytest-cov plugin
  - Integrates coverage.py with pytest
  - HTML reports, threshold enforcement

**Decision**: **pytest + pytest-cov + Textual's pilot mode**

**Rationale**:
- pytest is Python standard for testing (Constitution 2.1-2.7)
- Textual's pilot mode allows testing UI logic without actual terminal
- Layered testing approach:
  - **Unit tests (70%)**: Models, services, validation, currency logic
  - **Integration tests (20%)**: Repository + database, service workflows
  - **TUI tests (10%)**: Textual screens in pilot mode

**Alternatives Considered**:
- unittest: Less expressive than pytest, less ecosystem support
- Manual testing only: Violates constitution coverage requirements (2.1)

**Testing Structure**:
```python
# Unit test example
def test_bill_split_calculation():
    bill = Bill(items=[...], tax=Decimal('10.00'))
    splits = calculate_splits(bill)
    assert splits['user1'] == Decimal('25.50')

# Integration test example
def test_create_bill_updates_balances(db_connection):
    bill_service = BillService(db_connection)
    balance_service = BalanceService(db_connection)
    
    bill_service.create_bill(bill_data)
    balances = balance_service.get_all_balances()
    
    assert balances[('user1', 'user2')] == Decimal('25.50')

# TUI test example (Textual pilot mode)
async def test_user_list_screen():
    app = SplitfoolApp()
    async with app.run_test() as pilot:
        await pilot.press("u")  # Navigate to users
        assert isinstance(pilot.app.screen, UserManagementScreen)
```

**Coverage Targets**:
- Overall: 80% minimum (Constitution 2.1)
- Business logic (services, calculations): 95%+ (Constitution 2.1)
- Models: 90%+
- Repositories: 85%+
- UI screens: 60% (acceptable, focus on logic not rendering)

---

### 5. Textual Framework Best Practices

**Question**: What are the recommended patterns for building maintainable Textual TUI applications?

**Research Findings**:
- **Textual Architecture**:
  - App class: Main application controller
  - Screens: Full-screen views with lifecycle methods
  - Widgets: Reusable UI components with reactive properties
  - CSS: Styling system similar to web CSS

- **Best Practices** (from Textual docs):
  - Use reactive properties for state management
  - Compose complex screens from simple widgets
  - Separate business logic from UI logic
  - Use message passing for component communication
  - Implement proper keyboard shortcuts with bindings

- **Performance**:
  - Textual is async/await based (use asyncio)
  - Reactive updates are efficient (only re-renders changed widgets)
  - Workers for long-running tasks to keep UI responsive

**Decision**: **Follow Textual's recommended architecture with clean separation**

**Rationale**:
- Screens represent user stories (home, users, bills, balances, history, help)
- Widgets are reusable (UserList, BillForm, BalanceTable)
- Services handle business logic, UI just displays results
- Constitution alignment: separation of concerns (1.6), maintainability

**Key Patterns**:
```python
# Screen example
class BillEntryScreen(Screen):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save Bill"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield BillForm(id="bill-form")
        yield Footer()
    
    async def action_save(self) -> None:
        form_data = self.query_one("#bill-form").get_data()
        try:
            bill = await self.app.bill_service.create_bill(form_data)
            self.app.push_screen(SuccessScreen(f"Bill created: {bill.id}"))
        except ValidationError as e:
            self.notify(str(e), severity="error")

# Widget example with reactive state
class UserList(Widget):
    users: reactive[list[User]] = reactive(list)
    
    def watch_users(self, new_users: list[User]) -> None:
        # Re-render when users change
        self.refresh()
```

---

### 6. Error Handling and Validation Strategy

**Question**: How should we implement consistent error handling and validation across the application?

**Research Findings**:
- **Custom Exceptions** (Constitution 1.4):
  - Domain-specific exception hierarchy
  - Meaningful error messages with context
  - Error codes for consistency (Constitution 3.1)

- **Validation Approaches**:
  - Pydantic: Powerful validation, but adds dependency
  - Manual validation: Custom functions, more control
  - Dataclass validators: Python 3.11+ via `__post_init__`

**Decision**: **Custom exception hierarchy + manual validation functions**

**Rationale**:
- Pydantic adds unnecessary dependency (Constitution 1.5)
- Manual validation provides full control and clarity
- Custom exceptions provide domain-specific error handling
- Validation functions are testable in isolation

**Implementation**:
```python
# Custom exceptions (utils/errors.py)
class SplitfoolError(Exception):
    """Base exception for all Splitfool errors."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(SplitfoolError):
    """Raised when input validation fails."""
    pass

class UserNotFoundError(SplitfoolError):
    """Raised when user lookup fails."""
    pass

# Validation functions (services/validation.py)
def validate_user_name(name: str) -> None:
    """Validate user name is not empty and within length limits."""
    if not name or name.isspace():
        raise ValidationError(
            "User name cannot be empty.",
            code="USER_001"
        )
    if len(name) > 100:
        raise ValidationError(
            "User name must be 100 characters or less.",
            code="USER_002"
        )

def validate_bill_fractions(assignments: list[Assignment]) -> None:
    """Validate fractions sum to 1.0 for each item."""
    item_fractions: dict[int, Decimal] = {}
    for assignment in assignments:
        item_id = assignment.item_id
        item_fractions[item_id] = (
            item_fractions.get(item_id, Decimal('0')) + assignment.fraction
        )
    
    for item_id, total in item_fractions.items():
        if abs(total - Decimal('1.0')) > Decimal('0.001'):
            raise ValidationError(
                f"Item {item_id} fractions sum to {total}, must equal 1.0",
                code="BILL_001"
            )
```

---

## Summary of Decisions

| Topic | Decision | Primary Rationale |
|-------|----------|-------------------|
| Python Version | 3.11+ | Performance, modern syntax, stable |
| Database Access | Raw sqlite3 + Repository Pattern | Simplicity, standard library, sufficient for use case |
| Currency Handling | decimal.Decimal | Exact arithmetic, standard library, meets precision requirement |
| Testing Framework | pytest + pytest-cov + Textual pilot | Industry standard, constitution compliance, TUI testing support |
| TUI Architecture | Textual screens + widgets + services | Separation of concerns, maintainability, framework best practices |
| Error Handling | Custom exceptions + manual validation | Domain-specific, no extra dependencies, full control |

---

## Constitution Alignment Summary

✅ **Section I (Code Quality)**: All decisions prioritize type safety, documentation, security, and simplicity  
✅ **Section II (Testing)**: pytest with 80%+ coverage strategy defined  
✅ **Section III (UX)**: Error codes, validation, consistent terminology  
✅ **Section IV (Performance)**: Decimal precision sufficient, async architecture for responsiveness  
✅ **Section V (MCP)**: Not applicable  
✅ **Section VI (Governance)**: Decisions documented with rationale and alternatives

---

## Next Steps

With all clarifications resolved, proceed to **Phase 1: Design & Contracts**:
1. Create `data-model.md` with complete entity definitions
2. Generate API contracts (internal service interfaces)
3. Create `quickstart.md` with development setup instructions
4. Update agent context files
