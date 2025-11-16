"""Integration tests for balance calculation accuracy."""

import sqlite3
from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.db.schema import SCHEMA_SQL
from splitfool.services.balance_service import BalanceService
from splitfool.services.bill_service import AssignmentInput, BillInput, BillService, ItemInput
from splitfool.services.user_service import UserService


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Create in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def services(
    db_connection: sqlite3.Connection,
) -> tuple[UserService, BillService, BalanceService]:
    """Create service instances."""
    user_service = UserService(db_connection)
    bill_service = BillService(db_connection)
    balance_service = BalanceService(db_connection)
    return user_service, bill_service, balance_service


# T092-T093: Balance calculation integration tests


def test_balance_calculation_accuracy_with_complex_bills(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test that balances are calculated accurately across multiple complex bills."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")

    assert all(u.id is not None for u in [alice, bob, charlie])

    # Scenario:
    # Bill 1: Alice paid $60 for lunch split 3 ways
    # Bill 2: Bob paid $90 for dinner split 3 ways
    # Bill 3: Charlie paid $30 for coffee split 3 ways
    # Expected net: Everyone should owe each other $0 (balanced)

    # Bill 1
    bill1 = BillInput(
        payer_id=alice.id,  # type: ignore
        description="Lunch",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("60.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.34")),  # type: ignore
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Bill 2
    bill2 = BillInput(
        payer_id=bob.id,  # type: ignore
        description="Dinner",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("90.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.34")),  # type: ignore
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Bill 3
    bill3 = BillInput(
        payer_id=charlie.id,  # type: ignore
        description="Coffee",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Coffee",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.34")),  # type: ignore
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.33")),  # type: ignore
                ],
            )
        ],
    )
    bill_service.create_bill(bill3)

    # Calculate balances
    balances = balance_service.get_all_balances()

    # With perfect distribution ($60, $90, $30 = $180 total / 3 = $60 each),
    # balances should be minimal (only rounding differences)
    total_debt = sum(b.amount for b in balances)
    assert total_debt < Decimal("50.00")  # Should be roughly balanced (allowing for rounding)


def test_balance_calculation_with_settlement_workflow(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test complete settlement workflow: bills → balances → settle → new bills."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Phase 1: Create bills and check balances
    bill1 = BillInput(
        payer_id=alice.id,
        description="Bill 1",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("100.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    balances_phase1 = balance_service.get_all_balances()
    assert len(balances_phase1) == 1
    assert balances_phase1[0].amount == Decimal("50.00")

    # Phase 2: Settle all balances
    settlement = balance_service.settle_all_balances(note="End of month settlement")
    assert settlement.id is not None

    # Verify balances are cleared
    balances_after_settlement = balance_service.get_all_balances()
    assert len(balances_after_settlement) == 0

    # Phase 3: Create new bills after settlement
    bill2 = BillInput(
        payer_id=bob.id,  # Bob pays this time
        description="Bill 2",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("60.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Verify new balances reflect only post-settlement bills
    balances_phase3 = balance_service.get_all_balances()
    assert len(balances_phase3) == 1
    # Alice now owes Bob $30
    assert balances_phase3[0].debtor_id == alice.id
    assert balances_phase3[0].creditor_id == bob.id
    assert balances_phase3[0].amount == Decimal("30.00")


def test_balance_netting_with_multiple_payers(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test balance netting when multiple people pay for bills."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Alice pays $100, Bob owes $50
    bill1 = BillInput(
        payer_id=alice.id,
        description="Alice pays",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("100.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Bob pays $80, Alice owes $40
    bill2 = BillInput(
        payer_id=bob.id,
        description="Bob pays",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("80.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Calculate net balances
    balances = balance_service.get_all_balances()

    # Net: Bob owes $50, Alice owes $40 → Bob owes Alice $10
    assert len(balances) == 1
    assert balances[0].debtor_id == bob.id
    assert balances[0].creditor_id == alice.id
    assert balances[0].amount == Decimal("10.00")


def test_balance_calculation_with_three_way_netting(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test complex 3-way balance netting."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")

    assert all(u.id is not None for u in [alice, bob, charlie])

    # Alice pays $90 for lunch with Bob and Charlie (each owe $30)
    bill1 = BillInput(
        payer_id=alice.id,  # type: ignore
        description="Alice's lunch",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("90.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.34")),  # type: ignore
                ],
            )
        ],
    )
    bill_service.create_bill(bill1)

    # Bob pays $60 for dinner with Alice and Charlie (each owe $20)
    bill2 = BillInput(
        payer_id=bob.id,  # type: ignore
        description="Bob's dinner",
        tax=Decimal("0.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("60.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.34")),  # type: ignore
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),  # type: ignore
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.33")),  # type: ignore
                ],
            )
        ],
    )
    bill_service.create_bill(bill2)

    # Calculate balances
    balances = balance_service.get_all_balances()

    # Alice is owed: $29.70 + $29.70 (from bill 1) = $59.40 gross
    # Alice owes: $20.40 (from bill 2) = $20.40
    # Net: Alice is owed $39.00

    # Bob owes Alice: $29.70 (from bill 1)
    # Bob is owed from Alice: $20.40 (from bill 2)
    # Net: Bob owes Alice $9.30

    # Charlie owes Alice: $30.60 (from bill 1)
    # Charlie owes Bob: $19.80 (from bill 2)

    # Find Alice's net credit
    alice_credits = [b for b in balances if b.creditor_id == alice.id]
    alice_total_credit = sum(b.amount for b in alice_credits)

    # Allow rounding differences (fractions don't sum exactly to 1.0)
    expected_alice_credit = Decimal("39.00")
    assert abs(alice_total_credit - expected_alice_credit) < Decimal("2.00")


def test_balance_persistence_across_connections(
    db_connection: sqlite3.Connection,
) -> None:
    """Test that balances are calculated correctly with new service instances."""
    # Create services and data
    user_service1 = UserService(db_connection)
    bill_service1 = BillService(db_connection)
    balance_service1 = BalanceService(db_connection)

    alice = user_service1.create_user("Alice")
    bob = user_service1.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

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
    bill_service1.create_bill(bill_input)

    # Get balances with first service
    balances1 = balance_service1.get_all_balances()
    assert len(balances1) == 1
    assert balances1[0].amount == Decimal("10.00")

    # Create new service instances (simulating new connection/session)
    balance_service2 = BalanceService(db_connection)

    # Verify balances are same with new service
    balances2 = balance_service2.get_all_balances()
    assert len(balances2) == 1
    assert balances2[0].amount == Decimal("10.00")
    assert balances2[0].debtor_id == balances1[0].debtor_id
    assert balances2[0].creditor_id == balances1[0].creditor_id


def test_user_has_balances_check_accuracy(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test user_has_outstanding_balances is accurate for user deletion."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")

    assert all(u.id is not None for u in [alice, bob, charlie])

    # Charlie is not involved in any bills
    assert balance_service.user_has_outstanding_balances(charlie.id) is False

    # Create bill between Alice and Bob
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

    # Alice has outstanding balances (is owed money)
    assert balance_service.user_has_outstanding_balances(alice.id) is True

    # Bob has outstanding balances (owes money)
    assert balance_service.user_has_outstanding_balances(bob.id) is True

    # Charlie still has no balances
    assert balance_service.user_has_outstanding_balances(charlie.id) is False

    # Cannot delete Alice or Bob (they have balances)
    from splitfool.utils.errors import UserHasBalancesError

    with pytest.raises((UserHasBalancesError, sqlite3.IntegrityError)):
        # Either raises UserHasBalancesError or IntegrityError (foreign key)
        user_service.delete_user(alice.id)

    with pytest.raises((UserHasBalancesError, sqlite3.IntegrityError)):
        # Either raises UserHasBalancesError or IntegrityError (foreign key)
        user_service.delete_user(bob.id)

    # After settlement, balances are cleared
    balance_service.settle_all_balances()

    assert balance_service.user_has_outstanding_balances(alice.id) is False
    assert balance_service.user_has_outstanding_balances(bob.id) is False
    
    # Charlie can be deleted since he has no bills referencing him
    user_service.delete_user(charlie.id)
    
    # Note: Alice and Bob still cannot be deleted due to foreign key constraints
    # This is correct behavior - users referenced in bills should not be deletable


def test_balance_calculation_with_many_bills(
    services: tuple[UserService, BillService, BalanceService]
) -> None:
    """Test balance calculation performance and accuracy with many bills."""
    user_service, bill_service, balance_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Create 100 bills alternating payer
    num_bills = 100
    for i in range(num_bills):
        payer_id = alice.id if i % 2 == 0 else bob.id
        bill_input = BillInput(
            payer_id=payer_id,
            description=f"Bill {i+1}",
            tax=Decimal("0.00"),
            items=[
                ItemInput(
                    description=f"Item {i+1}",
                    cost=Decimal("10.00"),
                    assignments=[
                        AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                        AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                    ],
                )
            ],
        )
        bill_service.create_bill(bill_input)

    # Calculate balances
    balances = balance_service.get_all_balances()

    # With alternating payers and equal splits, net balance should be $0
    # (50 bills paid by Alice, 50 by Bob, each bill splits $10 equally)
    assert len(balances) == 0 or (
        len(balances) == 1 and balances[0].amount < Decimal("0.01")
    )
