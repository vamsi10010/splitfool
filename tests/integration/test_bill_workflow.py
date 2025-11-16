"""Integration tests for complete bill workflow."""

import sqlite3
from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.db.schema import SCHEMA_SQL
from splitfool.models.user import User
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
) -> tuple[UserService, BillService]:
    """Create service instances."""
    user_service = UserService(db_connection)
    bill_service = BillService(db_connection)
    return user_service, bill_service


# T074-T075: Complete bill workflow integration tests


def test_complete_bill_workflow_with_multiple_items(
    services: tuple[UserService, BillService]
) -> None:
    """Test complete workflow: create users, create bill, verify calculations."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")

    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None

    # Create bill with multiple items and various splits
    bill_input = BillInput(
        payer_id=alice.id,
        description="Dinner at Restaurant",
        tax=Decimal("15.00"),  # 15% tax
        items=[
            # Pizza split between Alice and Bob
            ItemInput(
                description="Pizza",
                cost=Decimal("30.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            ),
            # Salad for Charlie only
            ItemInput(
                description="Salad",
                cost=Decimal("20.00"),
                assignments=[AssignmentInput(user_id=charlie.id, fraction=Decimal("1.0"))],
            ),
            # Drinks split 3 ways
            ItemInput(
                description="Drinks",
                cost=Decimal("50.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.33")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.33")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.34")),
                ],
            ),
        ],
    )

    # Create the bill
    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Verify bill properties
    assert bill.payer_id == alice.id
    assert bill.description == "Dinner at Restaurant"
    assert bill.tax == Decimal("15.00")

    # Calculate total cost
    total = bill_service.calculate_total_cost(bill.id)
    assert total == Decimal("115.00")  # $30 + $20 + $50 + $15 tax

    # Calculate individual shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)
    charlie_share = bill_service.calculate_user_share(bill.id, charlie.id)

    # Alice: 50% of $30 = $15, 33% of $50 = $16.50 → subtotal $31.50
    # Tax: (31.50/100) * $15 = $4.725 → $4.73 rounded
    expected_alice = Decimal("36.23")

    # Bob: 50% of $30 = $15, 33% of $50 = $16.50 → subtotal $31.50
    # Tax: (31.50/100) * $15 = $4.725 → $4.73 rounded
    expected_bob = Decimal("36.23")

    # Charlie: 100% of $20 = $20, 34% of $50 = $17 → subtotal $37
    # Tax: (37/100) * $15 = $5.55
    expected_charlie = Decimal("42.55")

    # Allow small rounding differences
    assert abs(alice_share - expected_alice) < Decimal("0.01")
    assert abs(bob_share - expected_bob) < Decimal("0.01")
    assert abs(charlie_share - expected_charlie) < Decimal("0.01")

    # Verify shares sum to total
    total_shares = alice_share + bob_share + charlie_share
    assert abs(total_shares - total) < Decimal("0.02")


def test_bill_workflow_with_custom_fractions(
    services: tuple[UserService, BillService]
) -> None:
    """Test bill with custom fraction splits (not equal)."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Alice ate more, so gets larger fraction
    bill_input = BillInput(
        payer_id=alice.id,
        description="Unequal split meal",
        tax=Decimal("8.00"),
        items=[
            ItemInput(
                description="Food",
                cost=Decimal("40.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.7")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.3")),
                ],
            )
        ],
    )

    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Calculate shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)

    # Alice: 70% of $40 = $28, tax: 70% of $8 = $5.60 → $33.60
    assert alice_share == Decimal("33.60")

    # Bob: 30% of $40 = $12, tax: 30% of $8 = $2.40 → $14.40
    assert bob_share == Decimal("14.40")


def test_bill_workflow_single_user_item(
    services: tuple[UserService, BillService]
) -> None:
    """Test bill where one item is assigned to single user."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Bob ordered extra dessert just for himself
    bill_input = BillInput(
        payer_id=alice.id,
        description="Dinner with Bob's dessert",
        tax=Decimal("5.00"),
        items=[
            # Shared main course
            ItemInput(
                description="Main course",
                cost=Decimal("40.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            ),
            # Bob's dessert
            ItemInput(
                description="Dessert",
                cost=Decimal("10.00"),
                assignments=[AssignmentInput(user_id=bob.id, fraction=Decimal("1.0"))],
            ),
        ],
    )

    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Calculate shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)

    # Alice: 50% of $40 = $20, tax: (20/50) * $5 = $2 → $22
    assert alice_share == Decimal("22.00")

    # Bob: 50% of $40 = $20, 100% of $10 = $10 → $30, tax: (30/50) * $5 = $3 → $33
    assert bob_share == Decimal("33.00")

    # Total should be $55
    total = bill_service.calculate_total_cost(bill.id)
    assert total == Decimal("55.00")


def test_bill_workflow_tax_distribution_accuracy(
    services: tuple[UserService, BillService]
) -> None:
    """Test that tax is distributed proportionally and accurately."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")

    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None

    # Different cost items for each user
    bill_input = BillInput(
        payer_id=alice.id,
        description="Tax distribution test",
        tax=Decimal("10.00"),
        items=[
            ItemInput(
                description="Alice's item",
                cost=Decimal("10.00"),
                assignments=[AssignmentInput(user_id=alice.id, fraction=Decimal("1.0"))],
            ),
            ItemInput(
                description="Bob's item",
                cost=Decimal("20.00"),
                assignments=[AssignmentInput(user_id=bob.id, fraction=Decimal("1.0"))],
            ),
            ItemInput(
                description="Charlie's item",
                cost=Decimal("30.00"),
                assignments=[AssignmentInput(user_id=charlie.id, fraction=Decimal("1.0"))],
            ),
        ],
    )

    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Calculate shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)
    charlie_share = bill_service.calculate_user_share(bill.id, charlie.id)

    # Alice: $10 + (10/60) * $10 tax = $10 + $1.67 ≈ $11.67
    assert abs(alice_share - Decimal("11.67")) < Decimal("0.01")

    # Bob: $20 + (20/60) * $10 tax = $20 + $3.33 ≈ $23.33
    assert abs(bob_share - Decimal("23.33")) < Decimal("0.01")

    # Charlie: $30 + (30/60) * $10 tax = $30 + $5.00 = $35.00
    assert charlie_share == Decimal("35.00")

    # Total should equal bill total
    total = bill_service.calculate_total_cost(bill.id)
    assert total == Decimal("70.00")

    # Sum of shares should equal total (within rounding)
    total_shares = alice_share + bob_share + charlie_share
    assert abs(total_shares - total) < Decimal("0.01")


def test_bill_workflow_no_tax(services: tuple[UserService, BillService]) -> None:
    """Test bill with zero tax."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    bill_input = BillInput(
        payer_id=alice.id,
        description="No tax bill",
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

    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Calculate shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)

    # Each pays exactly half with no tax
    assert alice_share == Decimal("25.00")
    assert bob_share == Decimal("25.00")

    total = bill_service.calculate_total_cost(bill.id)
    assert total == Decimal("50.00")


def test_bill_workflow_retrieve_details(
    services: tuple[UserService, BillService]
) -> None:
    """Test retrieving complete bill details after creation."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Create bill
    bill_input = BillInput(
        payer_id=alice.id,
        description="Test bill",
        tax=Decimal("5.00"),
        items=[
            ItemInput(
                description="Pizza",
                cost=Decimal("20.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            ),
            ItemInput(
                description="Drinks",
                cost=Decimal("10.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            ),
        ],
    )

    created_bill = bill_service.create_bill(bill_input)
    assert created_bill.id is not None

    # Retrieve bill details
    bill_detail = bill_service.get_bill(created_bill.id)

    # Verify bill properties
    assert bill_detail.bill.id == created_bill.id
    assert bill_detail.bill.description == "Test bill"
    assert bill_detail.bill.tax == Decimal("5.00")
    assert bill_detail.payer_name == "Alice"

    # Verify items
    assert len(bill_detail.items) == 2
    item_descriptions = [item.description for item, _ in bill_detail.items]
    assert "Pizza" in item_descriptions
    assert "Drinks" in item_descriptions

    # Verify assignments for each item
    for item, assignments in bill_detail.items:
        assert len(assignments) == 2
        fractions = [a.fraction for a in assignments]
        assert Decimal("0.5") in fractions

    # Verify calculated shares
    assert alice.id in bill_detail.calculated_shares
    assert bob.id in bill_detail.calculated_shares

    # Alice's share: 50% of ($20 + $10) = $15, plus 50% of $5 tax = $2.50 → $17.50
    assert bill_detail.calculated_shares[alice.id] == Decimal("17.50")
    assert bill_detail.calculated_shares[bob.id] == Decimal("17.50")


def test_bill_workflow_preview_before_create(
    services: tuple[UserService, BillService]
) -> None:
    """Test previewing bill calculations before actually creating it."""
    user_service, bill_service = services

    # Create users
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")

    assert alice.id is not None
    assert bob.id is not None

    # Create bill input
    bill_input = BillInput(
        payer_id=alice.id,
        description="Preview test",
        tax=Decimal("8.00"),
        items=[
            ItemInput(
                description="Item",
                cost=Decimal("40.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            )
        ],
    )

    # Preview without creating
    preview = bill_service.preview_bill(bill_input)

    # Verify preview data
    assert preview.description == "Preview test"
    assert preview.payer_name == "Alice"
    assert preview.subtotal == Decimal("40.00")
    assert preview.tax == Decimal("8.00")
    assert preview.total == Decimal("48.00")

    # Verify user shares in preview
    assert "Alice" in preview.user_shares
    assert "Bob" in preview.user_shares
    assert preview.user_shares["Alice"] == Decimal("24.00")
    assert preview.user_shares["Bob"] == Decimal("24.00")

    # Verify bill was NOT actually created
    from splitfool.db.repositories.bill_repository import BillRepository

    bill_repo = BillRepository(user_service.conn)
    all_bills = bill_repo.get_all()
    assert len(all_bills) == 0


def test_complex_bill_scenario(services: tuple[UserService, BillService]) -> None:
    """Test complex real-world bill scenario."""
    user_service, bill_service = services

    # Create group of friends
    alice = user_service.create_user("Alice")
    bob = user_service.create_user("Bob")
    charlie = user_service.create_user("Charlie")
    diana = user_service.create_user("Diana")

    assert all(u.id is not None for u in [alice, bob, charlie, diana])

    # Complex dinner bill:
    # - Appetizers shared by all 4
    # - Alice and Bob split a main course
    # - Charlie has his own main
    # - Diana and Alice split dessert
    # - Everyone shares drinks
    bill_input = BillInput(
        payer_id=alice.id,
        description="Group dinner",
        tax=Decimal("25.00"),
        items=[
            # Appetizers for 4
            ItemInput(
                description="Appetizers",
                cost=Decimal("40.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=diana.id, fraction=Decimal("0.25")),
                ],
            ),
            # Alice and Bob's shared main
            ItemInput(
                description="Main course (A&B)",
                cost=Decimal("60.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.5")),
                ],
            ),
            # Charlie's main
            ItemInput(
                description="Main course (C)",
                cost=Decimal("35.00"),
                assignments=[AssignmentInput(user_id=charlie.id, fraction=Decimal("1.0"))],
            ),
            # Alice and Diana's dessert
            ItemInput(
                description="Dessert",
                cost=Decimal("15.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.5")),
                    AssignmentInput(user_id=diana.id, fraction=Decimal("0.5")),
                ],
            ),
            # Drinks for all
            ItemInput(
                description="Drinks",
                cost=Decimal("50.00"),
                assignments=[
                    AssignmentInput(user_id=alice.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=bob.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=charlie.id, fraction=Decimal("0.25")),
                    AssignmentInput(user_id=diana.id, fraction=Decimal("0.25")),
                ],
            ),
        ],
    )

    bill = bill_service.create_bill(bill_input)
    assert bill.id is not None

    # Calculate shares
    alice_share = bill_service.calculate_user_share(bill.id, alice.id)
    bob_share = bill_service.calculate_user_share(bill.id, bob.id)
    charlie_share = bill_service.calculate_user_share(bill.id, charlie.id)
    diana_share = bill_service.calculate_user_share(bill.id, diana.id)

    # Verify total
    total = bill_service.calculate_total_cost(bill.id)
    assert total == Decimal("225.00")  # $200 food + $25 tax

    # Verify all shares sum to total
    total_shares = alice_share + bob_share + charlie_share + diana_share
    assert abs(total_shares - total) < Decimal("0.05")

    # Alice should have highest share (appetizer + half main + half dessert + drinks)
    # Alice: $10 + $30 + $7.50 + $12.50 = $60 subtotal
    # Tax: (60/200) * $25 = $7.50
    # Total: $67.50
    assert abs(alice_share - Decimal("67.50")) < Decimal("0.01")
