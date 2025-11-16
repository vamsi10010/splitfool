"""Unit tests for BalanceService."""

import sqlite3
from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.models.user import User
from splitfool.services.balance_service import BalanceService
from splitfool.services.bill_service import AssignmentInput, BillInput, BillService, ItemInput


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Create in-memory database for testing."""
    from splitfool.db.schema import SCHEMA_SQL

    conn = sqlite3.Connection(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def balance_service(db_connection: sqlite3.Connection) -> BalanceService:
    """Create BalanceService instance."""
    return BalanceService(db_connection)


@pytest.fixture
def bill_service(db_connection: sqlite3.Connection) -> BillService:
    """Create BillService instance."""
    return BillService(db_connection)


@pytest.fixture
def sample_users(db_connection: sqlite3.Connection) -> list[User]:
    """Create sample users for testing."""
    from splitfool.db.repositories.user_repository import UserRepository

    repo = UserRepository(db_connection)
    alice = repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    bob = repo.create(User(id=None, name="Bob", created_at=datetime.now()))
    charlie = repo.create(User(id=None, name="Charlie", created_at=datetime.now()))
    return [alice, bob, charlie]


# T090: Test BalanceService.get_all_balances()


def test_get_all_balances_empty_database(balance_service: BalanceService) -> None:
    """Test getting balances when no bills exist."""
    balances = balance_service.get_all_balances()
    assert balances == []


def test_get_all_balances_single_bill_equal_split(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test balances with single bill split equally."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid $30 for pizza split equally with Bob
    bill_input = BillInput(
        payer_id=alice.id,
        description="Pizza",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Pizza",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    balances = balance_service.get_all_balances()

    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("15.00")


def test_get_all_balances_with_tax_distribution(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test balances with tax distributed proportionally."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid $20 + $10 tax, split equally
    bill_input = BillInput(
        payer_id=alice.id,
        description="Dinner with tax",
        tax=Decimal("10.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    balances = balance_service.get_all_balances()

    # Bob owes 50% of $20 + 50% of $10 tax = $15
    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("15.00")


def test_get_all_balances_unequal_split(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test balances with unequal split."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid $100, Bob gets 75%, Alice gets 25%
    bill_input = BillInput(
        payer_id=alice.id,
        description="Unequal split",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Expensive item",
                cost=Decimal("100.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.75")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    balances = balance_service.get_all_balances()

    # Bob owes 75% = $75
    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("75.00")


def test_get_all_balances_multiple_bills_accumulate(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that multiple bills accumulate balances."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # First bill: Alice paid $20, split equally
    bill1 = BillInput(
        payer_id=alice.id,
        description="Bill 1",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Second bill: Alice paid $30, split equally
    bill2 = BillInput(
        payer_id=alice.id,
        description="Bill 2",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    balances = balance_service.get_all_balances()

    # Bob owes $10 + $15 = $25 total
    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("25.00")


def test_get_all_balances_nets_mutual_debts(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that mutual debts are netted out."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Bill 1: Alice paid $50, Bob owes $25
    bill1 = BillInput(
        payer_id=alice.id,
        description="Alice pays",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("50.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Bill 2: Bob paid $30, Alice owes $15
    bill2 = BillInput(
        payer_id=bob.id,
        description="Bob pays",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    balances = balance_service.get_all_balances()

    # Net: Bob owes $25, Alice owes $15 → Bob owes Alice $10
    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("10.00")


def test_get_all_balances_three_users(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test balances with three users."""
    alice, bob, charlie = sample_users
    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None

    # Alice paid $30 for pizza split 3 ways
    bill_input = BillInput(
        payer_id=alice.id,
        description="Pizza",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Pizza",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.33")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.34")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    balances = balance_service.get_all_balances()

    assert len(balances) == 2
    # Bob owes Alice $9.90
    bob_debt = next((b for b in balances if b.debtor_id == bob.id), None)
    assert bob_debt is not None
    assert bob_debt.creditor_id == alice.id
    assert bob_debt.amount == Decimal("9.90")

    # Charlie owes Alice $10.20
    charlie_debt = next((b for b in balances if b.debtor_id == charlie.id), None)
    assert charlie_debt is not None
    assert charlie_debt.creditor_id == alice.id
    assert charlie_debt.amount == Decimal("10.20")


def test_get_all_balances_ignores_payer_own_share(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that payer doesn't owe themselves."""
    alice = sample_users[0]
    assert alice.id is not None

    # Alice paid $20 for herself only
    bill_input = BillInput(
        payer_id=alice.id,
        description="Solo purchase",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[AssignmentInput(user_id=alice.id, fraction=Decimal("1.0"))],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    balances = balance_service.get_all_balances()

    # No balances since Alice paid for herself
    assert balances == []


# T091: Test BalanceService.get_user_balances()


def test_get_user_balances_no_balances(
    balance_service: BalanceService, sample_users: list[User]
) -> None:
    """Test getting user balances when none exist."""
    alice = sample_users[0]
    assert alice.id is not None

    debts, credits = balance_service.get_user_balances(alice.id)

    assert debts == []
    assert credits == []


def test_get_user_balances_only_debts(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test user with only debts."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid, Bob owes
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    debts, credits = balance_service.get_user_balances(bob.id)

    assert len(debts) == 1
    assert debts[0].amount == Decimal("10.00")
    assert credits == []


def test_get_user_balances_only_credits(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test user with only credits."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid, Bob owes
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    debts, credits = balance_service.get_user_balances(alice.id)

    assert debts == []
    assert len(credits) == 1
    assert credits[0].amount == Decimal("10.00")


def test_get_user_balances_both_debts_and_credits(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test user with both debts and credits."""
    alice, bob, charlie = sample_users
    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None

    # Bill 1: Alice paid, Bob owes Alice $10
    bill1 = BillInput(
        payer_id=alice.id,
        description="Bill 1",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Bill 2: Bob paid, Alice owes Bob $5
    bill2 = BillInput(
        payer_id=bob.id,
        description="Bill 2",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("10.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Bill 3: Charlie paid, Alice owes Charlie $15
    bill3 = BillInput(
        payer_id=charlie.id,
        description="Bill 3",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill3)

    debts, credits = balance_service.get_user_balances(alice.id)

    # Alice has net debt to Charlie ($15) and net credit from Bob ($5)
    # After netting Bill1 and Bill2: Bob owes Alice $5 net
    # Alice owes Charlie $15

    # Debts: Alice owes Charlie
    assert len(debts) >= 1
    charlie_debt = next((d for d in debts if d.creditor_id == charlie.id), None)
    assert charlie_debt is not None
    assert charlie_debt.amount == Decimal("15.00")


# T091: Test BalanceService.user_has_outstanding_balances()


def test_user_has_outstanding_balances_false_when_no_balances(
    balance_service: BalanceService, sample_users: list[User]
) -> None:
    """Test that user without balances returns False."""
    alice = sample_users[0]
    assert alice.id is not None

    assert balance_service.user_has_outstanding_balances(alice.id) is False


def test_user_has_outstanding_balances_true_with_debts(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that user with debts returns True."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid, Bob owes
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    assert balance_service.user_has_outstanding_balances(bob.id) is True


def test_user_has_outstanding_balances_true_with_credits(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that user with credits returns True."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Alice paid, Bob owes
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    assert balance_service.user_has_outstanding_balances(alice.id) is True


# T091: Test BalanceService.preview_settlement()


def test_preview_settlement_empty(balance_service: BalanceService) -> None:
    """Test preview with no balances."""
    preview = balance_service.preview_settlement()

    assert preview.balances == []
    assert preview.total_debts == Decimal("0")


def test_preview_settlement_with_balances(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test preview with existing balances."""
    alice, bob, charlie = sample_users
    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None

    # Create bills with various balances
    bill1 = BillInput(
        payer_id=alice.id,
        description="Bill 1",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    bill2 = BillInput(
        payer_id=alice.id,
        description="Bill 2",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("40.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    preview = balance_service.preview_settlement()

    assert len(preview.balances) == 2
    # Total debts: Bob owes $15 + Charlie owes $20 = $35
    assert preview.total_debts == Decimal("35.00")


# T091: Test BalanceService.settle_all_balances()


def test_settle_all_balances_creates_settlement(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that settlement is created."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Create a bill
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    # Settle
    settlement = balance_service.settle_all_balances(note="Test settlement")

    assert settlement.id is not None
    assert settlement.note == "Test settlement"
    assert settlement.settled_at is not None


def test_settle_all_balances_clears_balances(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that settlement clears all balances."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Create a bill
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill_input)

    # Verify balance exists
    balances_before = balance_service.get_all_balances()
    assert len(balances_before) == 1

    # Settle
    balance_service.settle_all_balances()

    # Verify balances cleared
    balances_after = balance_service.get_all_balances()
    assert balances_after == []


def test_settle_all_balances_preserves_bills(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
    db_connection: sqlite3.Connection,
) -> None:
    """Test that settlement preserves bill history."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Create a bill
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    created_bill = bill_service.create_bill(bill_input)

    # Settle
    balance_service.settle_all_balances()

    # Verify bill still exists
    bill_detail = bill_service.get_bill(created_bill.id)  # type: ignore
    assert bill_detail.bill.id == created_bill.id


def test_new_bills_after_settlement_create_new_balances(
    balance_service: BalanceService,
    bill_service: BillService,
    sample_users: list[User],
) -> None:
    """Test that bills after settlement create new balances."""
    alice, bob, _ = sample_users
    assert alice.id is not None
    assert bob.id is not None

    # Create and settle first bill
    bill1 = BillInput(
        payer_id=alice.id,
        description="Bill 1",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)
    balance_service.settle_all_balances()

    # Verify balances cleared
    assert balance_service.get_all_balances() == []

    # Create new bill after settlement
    bill2 = BillInput(
        payer_id=alice.id,
        description="Bill 2",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Verify new balance exists
    balances = balance_service.get_all_balances()
    assert len(balances) == 1
    assert balances[0].amount == Decimal("15.00")


# T091: Test BalanceService.get_last_settlement()


def test_get_last_settlement_none_when_empty(balance_service: BalanceService) -> None:
    """Test getting last settlement when none exist."""
    settlement = balance_service.get_last_settlement()
    assert settlement is None


def test_get_last_settlement_returns_most_recent(
    balance_service: BalanceService,
) -> None:
    """Test that get_last_settlement returns the most recent."""
    # Create first settlement
    settlement1 = balance_service.settle_all_balances(note="First")

    # Create second settlement
    settlement2 = balance_service.settle_all_balances(note="Second")

    # Get last should return second
    last = balance_service.get_last_settlement()
    assert last is not None
    assert last.id == settlement2.id
    assert last.note == "Second"
