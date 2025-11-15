# Data Model: Splitfool

**Feature**: 001-tui-bill-splitter  
**Date**: 2025-11-15  
**Status**: Final Design

## Overview

This document defines the complete data model for Splitfool, including entities, relationships, validation rules, and state transitions. The model uses Python dataclasses with frozen=True for immutability (Constitution 1.9), SQLite for persistence, and Decimal for currency precision.

---

## Entity Definitions

### 1. User

Represents a person participating in bill splitting.

**Purpose**: Track participants who can pay bills or have items assigned to them.

**Python Model**:
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    """Immutable user entity."""
    id: int | None  # None for new users, int after DB insert
    name: str
    created_at: datetime
    
    def __post_init__(self) -> None:
        """Validate user data on creation."""
        if not self.name or self.name.isspace():
            raise ValueError("User name cannot be empty")
        if len(self.name) > 100:
            raise ValueError("User name must be 100 characters or less")
```

**Database Schema**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_name ON users(name);
```

**Validation Rules**:
- `name`: Required, non-empty, non-whitespace, max 100 characters, unique (FR-006, FR-007)
- `created_at`: Auto-generated on creation

**Business Rules**:
- Users cannot be deleted if they have outstanding balances (FR-004)
- User names must be unique across the system (FR-007)

---

### 2. Bill

Represents a single expense event with multiple line items.

**Purpose**: Container for grouped expenses with a designated payer and timestamp.

**Python Model**:
```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class Bill:
    """Immutable bill entity."""
    id: int | None
    payer_id: int  # Foreign key to users.id
    description: str
    tax: Decimal  # Additional costs (tax, tip, fees)
    created_at: datetime
    
    def __post_init__(self) -> None:
        """Validate bill data."""
        if self.tax < Decimal('0'):
            raise ValueError("Tax must be non-negative")
        if len(self.description) > 500:
            raise ValueError("Description must be 500 characters or less")
```

**Database Schema**:
```sql
CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payer_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    tax REAL NOT NULL CHECK(tax >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payer_id) REFERENCES users(id)
);

CREATE INDEX idx_bills_payer_id ON bills(payer_id);
CREATE INDEX idx_bills_created_at ON bills(created_at DESC);
```

**Validation Rules**:
- `payer_id`: Required, must reference existing user (FR-016)
- `description`: Required, max 500 characters
- `tax`: Non-negative decimal (FR-014, FR-022)
- `created_at`: Auto-generated timestamp

**Business Rules**:
- Bill must have at least one item before finalization (FR-049)
- At least one user must be assigned to items (FR-050)
- Tax is distributed proportionally across users based on subtotal share (FR-015)

**Relationships**:
- Many-to-one with User (payer)
- One-to-many with Item

---

### 3. Item

Represents a single line item within a bill.

**Purpose**: Individual expense that can be split among users with custom fractions.

**Python Model**:
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Item:
    """Immutable item entity."""
    id: int | None
    bill_id: int  # Foreign key to bills.id
    description: str
    cost: Decimal
    
    def __post_init__(self) -> None:
        """Validate item data."""
        if self.cost <= Decimal('0'):
            raise ValueError("Item cost must be positive")
        if len(self.description) > 200:
            raise ValueError("Description must be 200 characters or less")
```

**Database Schema**:
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL CHECK(cost > 0),
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
);

CREATE INDEX idx_items_bill_id ON items(bill_id);
```

**Validation Rules**:
- `bill_id`: Required, must reference existing bill
- `description`: Required, max 200 characters
- `cost`: Positive decimal (FR-009, FR-022, FR-048)

**Business Rules**:
- Each item must have at least one assignment (user) (FR-010)
- Assignments for an item must have fractions summing to 1.0 (FR-013)

**Relationships**:
- Many-to-one with Bill
- One-to-many with Assignment

---

### 4. Assignment

Represents the relationship between an item and a user with a fraction.

**Purpose**: Define how much of an item's cost each user is responsible for.

**Python Model**:
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Assignment:
    """Immutable assignment entity."""
    id: int | None
    item_id: int  # Foreign key to items.id
    user_id: int  # Foreign key to users.id
    fraction: Decimal  # Portion of item cost (0.0 to 1.0)
    
    def __post_init__(self) -> None:
        """Validate assignment data."""
        if not (Decimal('0') < self.fraction <= Decimal('1')):
            raise ValueError("Fraction must be between 0 and 1")
```

**Database Schema**:
```sql
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    fraction REAL NOT NULL CHECK(fraction > 0 AND fraction <= 1),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(item_id, user_id)
);

CREATE INDEX idx_assignments_item_id ON assignments(item_id);
CREATE INDEX idx_assignments_user_id ON assignments(user_id);
```

**Validation Rules**:
- `item_id`: Required, must reference existing item
- `user_id`: Required, must reference existing user
- `fraction`: Decimal between 0 (exclusive) and 1 (inclusive) (FR-012)
- Unique constraint: One assignment per item-user pair

**Business Rules**:
- For each item, all assignments' fractions must sum to 1.0 (±0.001 tolerance) (FR-013)
- Default to equal split when multiple users assigned (FR-011)
- Cannot assign item to zero users (FR-050)

**Relationships**:
- Many-to-one with Item
- Many-to-one with User

---

### 5. Balance

Represents the net amount one user owes to another.

**Purpose**: Calculated view of debt relationships between users based on finalized bills.

**Note**: Balance is a **derived entity** calculated from bills, not stored directly. The balance calculation happens on-demand.

**Python Model**:
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Balance:
    """Immutable balance entity (derived, not stored)."""
    debtor_id: int  # User who owes money
    creditor_id: int  # User who is owed money
    amount: Decimal  # Net amount owed (positive)
    
    def __post_init__(self) -> None:
        """Validate balance data."""
        if self.amount <= Decimal('0'):
            raise ValueError("Balance amount must be positive")
        if self.debtor_id == self.creditor_id:
            raise ValueError("Debtor and creditor must be different users")
```

**Calculation Logic**:
```python
def calculate_balances(bills: list[Bill], items: list[Item], 
                       assignments: list[Assignment]) -> list[Balance]:
    """
    Calculate net balances between all users.
    
    Algorithm:
    1. For each bill, calculate each user's share (items + proportional tax)
    2. Track what each user owes the payer
    3. Net out mutual debts (if A owes B $50 and B owes A $30, result: A owes B $20)
    4. Return only non-zero balances
    """
    # Detailed implementation in services/balance_service.py
    pass
```

**Business Rules**:
- Balances are always "net" - mutual debts are simplified (FR-025)
- Only positive balances are shown (if net is zero, no balance entry)
- Balances update automatically when bills are finalized (FR-020)
- All balances cleared when settlement performed (FR-028)

**UI Display** (FR-024):
```
Outstanding Balances:
  Alice owes Bob: $45.50
  Charlie owes Bob: $23.00
  Alice owes Charlie: $12.75
```

---

### 6. Settlement

Represents a bulk action that resets all balances to zero.

**Purpose**: Record when all debts were cleared, allowing sync with external payment tracking.

**Python Model**:
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Settlement:
    """Immutable settlement record."""
    id: int | None
    settled_at: datetime
    note: str  # Optional user note about settlement
```

**Database Schema**:
```sql
CREATE TABLE settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);

CREATE INDEX idx_settlements_settled_at ON settlements(settled_at DESC);
```

**Business Rules**:
- Settlement is all-or-nothing: clears ALL balances, not individual ones (FR-026)
- Confirmation required before settlement (FR-027)
- Bills remain in history after settlement (for audit trail)
- Balances calculated from bills created after most recent settlement

**Settlement Logic**:
```python
def settle_all_balances() -> Settlement:
    """
    Create settlement record. Balances will be calculated only from bills
    created after this settlement timestamp.
    
    Note: Does NOT delete bills or create offsetting transactions.
    Simply records a cutoff point for balance calculations.
    """
    settlement = Settlement(
        id=None,
        settled_at=datetime.now(),
        note="All balances settled"
    )
    # Insert into database
    return settlement
```

---

## Entity Relationships Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     │ 1:N (payer)
     ↓
┌──────────┐
│   Bill   │◄─────────┐
└────┬─────┘          │
     │                │
     │ 1:N            │ Settlement affects
     ↓                │ balance calculation
┌──────────┐          │
│   Item   │          │
└────┬─────┘          │
     │                │
     │ 1:N            │
     ↓                │
┌──────────────┐      │
│ Assignment   │      │
└────┬─────────┘      │
     │                │
     │ N:1            │
     ↓                │
┌──────────┐          │
│   User   │          │
└──────────┘          │
     ↓                │
  (derives)           │
┌──────────┐          │
│ Balance  │◄─────────┘
└──────────┘
     ↑
  (clears)
┌──────────────┐
│  Settlement  │
└──────────────┘
```

---

## Data Flow: Creating a Bill

**Scenario**: Alice paid $100 for dinner. Bill has 2 items: Pizza ($60) split between Alice and Bob, and Salad ($40) for Bob only. Tax is $10.

**Step-by-Step Data Flow**:

1. **User creates bill** (UI → Bill Service):
   ```python
   bill_data = BillInput(
       payer_id=1,  # Alice
       description="Dinner at Pizza Place",
       tax=Decimal('10.00'),
       items=[
           ItemInput(description="Pizza", cost=Decimal('60.00'),
                    assignments=[
                        AssignmentInput(user_id=1, fraction=Decimal('0.5')),  # Alice
                        AssignmentInput(user_id=2, fraction=Decimal('0.5'))   # Bob
                    ]),
           ItemInput(description="Salad", cost=Decimal('40.00'),
                    assignments=[
                        AssignmentInput(user_id=2, fraction=Decimal('1.0'))   # Bob only
                    ])
       ]
   )
   ```

2. **Validation** (Bill Service):
   - Verify payer exists
   - Verify all assigned users exist
   - Verify item costs are positive
   - Verify fractions sum to 1.0 for each item
   - Verify at least one item exists

3. **Calculate user shares** (Balance Service):
   ```
   Subtotal: $100.00
   Tax: $10.00
   Total: $110.00
   
   Alice's share:
     - Pizza: $60.00 × 0.5 = $30.00
     - Salad: $0.00
     - Subtotal: $30.00
     - Tax share: $10.00 × ($30.00 / $100.00) = $3.00
     - Total: $33.00
   
   Bob's share:
     - Pizza: $60.00 × 0.5 = $30.00
     - Salad: $40.00 × 1.0 = $40.00
     - Subtotal: $70.00
     - Tax share: $10.00 × ($70.00 / $100.00) = $7.00
     - Total: $77.00
   
   Alice paid: $110.00
   Alice owes: $33.00
   Net: Alice is owed $77.00 by Bob
   ```

4. **Persist to database** (Repository Layer):
   ```sql
   -- Transaction begins
   INSERT INTO bills (payer_id, description, tax) VALUES (1, 'Dinner at Pizza Place', 10.00);
   -- bill_id = 1
   
   INSERT INTO items (bill_id, description, cost) VALUES (1, 'Pizza', 60.00);
   -- item_id = 1
   INSERT INTO items (bill_id, description, cost) VALUES (1, 'Salad', 40.00);
   -- item_id = 2
   
   INSERT INTO assignments (item_id, user_id, fraction) VALUES (1, 1, 0.5);  -- Alice, Pizza
   INSERT INTO assignments (item_id, user_id, fraction) VALUES (1, 2, 0.5);  -- Bob, Pizza
   INSERT INTO assignments (item_id, user_id, fraction) VALUES (2, 2, 1.0);  -- Bob, Salad
   -- Transaction commits
   ```

5. **Update UI** (TUI):
   - Show success message
   - Return to home screen
   - Balance view now shows: "Bob owes Alice: $77.00"

---

## State Transitions

### User Lifecycle
```
[Not Exists] --create--> [Active] --delete--> [Deleted]
                           ↑         ↓
                           └─ [Error: Has balances]
```

### Bill Lifecycle
```
[Draft] --add items--> [Draft with Items] --finalize--> [Finalized]
   ↑                          ↑
   └─ [Error: Validation]──────┘

Note: No "editing" state after finalization (out of scope: FR not defined)
```

### Balance Lifecycle
```
[Zero] --bill finalized--> [Positive] --settlement--> [Zero]
         ↑                     ↓
         └──────[Calculate]────┘
```

---

## Validation Rules Summary

| Entity | Field | Rules | Error Code |
|--------|-------|-------|------------|
| User | name | Non-empty, non-whitespace, max 100 chars, unique | USER_001, USER_002, USER_003 |
| User | (deletion) | Cannot delete if has outstanding balances | USER_004 |
| Bill | payer_id | Must exist in users table | BILL_002 |
| Bill | tax | Non-negative | BILL_003 |
| Bill | (items) | Must have at least one item | BILL_004 |
| Item | cost | Positive number | ITEM_001 |
| Item | description | Non-empty, max 200 chars | ITEM_002 |
| Assignment | fraction | 0 < fraction ≤ 1.0 | ASSIGN_001 |
| Assignment | (per item) | Fractions must sum to 1.0 (±0.001) | ASSIGN_002 |
| Assignment | (per item) | Must have at least one assignment | ASSIGN_003 |

---

## Performance Considerations

### Indexing Strategy
- **Primary keys**: Auto-indexed by SQLite
- **Foreign keys**: Indexed for JOIN performance (users.id, bills.id, items.id)
- **Query patterns**:
  - Get all bills for a user: `idx_bills_payer_id`
  - Get recent bills: `idx_bills_created_at`
  - Get items for a bill: `idx_items_bill_id`
  - Get assignments for item/user: `idx_assignments_item_id`, `idx_assignments_user_id`

### Query Optimization
- Use `JOIN` to fetch bill with items and assignments in single query
- Calculate balances in-memory after fetching all relevant bills (post-settlement)
- Pagination for bill history if >1000 bills (FR requirement: handle 1000+ bills)

### Scalability (Constitution 4.3)
- Expected data volume (from SC-008):
  - 100 users
  - 1000 bills
  - 10,000 items (avg 10 items/bill)
  - ~20,000 assignments (avg 2 users/item)
- SQLite can handle this easily (millions of rows supported)
- No caching needed at this scale
- All queries should complete in <50ms (Constitution 4.1)

---

## Database Initialization

**Schema Creation Script** (`db/schema.py`):
```python
SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payer_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    tax REAL NOT NULL CHECK(tax >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payer_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_bills_payer_id ON bills(payer_id);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at DESC);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL CHECK(cost > 0),
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_items_bill_id ON items(bill_id);

-- Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    fraction REAL NOT NULL CHECK(fraction > 0 AND fraction <= 1),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(item_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_assignments_item_id ON assignments(item_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user_id ON assignments(user_id);

-- Settlements table
CREATE TABLE IF NOT EXISTS settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);
CREATE INDEX IF NOT EXISTS idx_settlements_settled_at ON settlements(settled_at DESC);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO schema_version (version) VALUES (1);
"""

def initialize_database(db_path: str) -> None:
    """Initialize database with schema."""
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
```

---

## Summary

This data model provides:
- ✅ **6 entities**: User, Bill, Item, Assignment, Balance (derived), Settlement
- ✅ **Immutable dataclasses** with validation (Constitution 1.9)
- ✅ **SQLite schema** with proper indexing (Constitution 4.4)
- ✅ **Clear relationships** and business rules
- ✅ **Decimal precision** for currency (Constitution requirement)
- ✅ **Type safety** throughout (Constitution 1.2)
- ✅ **Comprehensive validation** rules (Constitution 1.4, Section III)

**Next**: Generate API contracts (service interfaces) in `/contracts/` directory.
