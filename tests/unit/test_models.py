"""Unit tests for data models."""

from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.models import Assignment, Balance, Bill, Item, Settlement, User


def test_user_validation_rejects_empty_name() -> None:
    """Test that User rejects empty name."""
    with pytest.raises(ValueError, match="cannot be empty"):
        User(id=None, name="", created_at=datetime.now())


def test_user_validation_rejects_whitespace_name() -> None:
    """Test that User rejects whitespace-only name."""
    with pytest.raises(ValueError, match="cannot be empty"):
        User(id=None, name="   ", created_at=datetime.now())


def test_user_validation_rejects_name_too_long() -> None:
    """Test that User rejects name over 100 characters."""
    with pytest.raises(ValueError, match="100 characters or less"):
        User(id=None, name="A" * 101, created_at=datetime.now())


def test_user_validation_accepts_valid_name() -> None:
    """Test that User accepts valid names."""
    user = User(id=None, name="Alice", created_at=datetime.now())
    assert user.name == "Alice"


def test_user_is_frozen() -> None:
    """Test that User is immutable."""
    user = User(id=None, name="Alice", created_at=datetime.now())
    with pytest.raises(AttributeError):
        user.name = "Bob"  # type: ignore


def test_bill_validation_rejects_negative_tax() -> None:
    """Test that Bill rejects negative tax."""
    with pytest.raises(ValueError, match="Tax must be non-negative"):
        Bill(
            id=None,
            payer_id=1,
            description="Test",
            tax=Decimal("-1.00"),
            created_at=datetime.now(),
        )


def test_bill_validation_accepts_zero_tax() -> None:
    """Test that Bill accepts zero tax."""
    bill = Bill(
        id=None,
        payer_id=1,
        description="Test",
        tax=Decimal("0.00"),
        created_at=datetime.now(),
    )
    assert bill.tax == Decimal("0.00")


def test_bill_validation_rejects_description_too_long() -> None:
    """Test that Bill rejects description over 500 characters."""
    with pytest.raises(ValueError, match="500 characters or less"):
        Bill(
            id=None,
            payer_id=1,
            description="A" * 501,
            tax=Decimal("0.00"),
            created_at=datetime.now(),
        )


def test_item_validation_rejects_non_positive_cost() -> None:
    """Test that Item rejects non-positive cost."""
    with pytest.raises(ValueError, match="must be positive"):
        Item(id=None, bill_id=1, description="Test", cost=Decimal("0.00"))
    
    with pytest.raises(ValueError, match="must be positive"):
        Item(id=None, bill_id=1, description="Test", cost=Decimal("-1.00"))


def test_item_validation_accepts_positive_cost() -> None:
    """Test that Item accepts positive cost."""
    item = Item(id=None, bill_id=1, description="Test", cost=Decimal("10.00"))
    assert item.cost == Decimal("10.00")


def test_item_validation_rejects_description_too_long() -> None:
    """Test that Item rejects description over 200 characters."""
    with pytest.raises(ValueError, match="200 characters or less"):
        Item(id=None, bill_id=1, description="A" * 201, cost=Decimal("10.00"))


def test_assignment_validation_rejects_fraction_out_of_range() -> None:
    """Test that Assignment rejects fraction outside (0, 1]."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.0"))
    
    with pytest.raises(ValueError, match="between 0 and 1"):
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("-0.1"))
    
    with pytest.raises(ValueError, match="between 0 and 1"):
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("1.1"))


def test_assignment_validation_accepts_valid_fraction() -> None:
    """Test that Assignment accepts valid fractions."""
    assignment = Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.5"))
    assert assignment.fraction == Decimal("0.5")
    
    assignment = Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("1.0"))
    assert assignment.fraction == Decimal("1.0")


def test_balance_validation_rejects_non_positive_amount() -> None:
    """Test that Balance rejects non-positive amount."""
    with pytest.raises(ValueError, match="must be positive"):
        Balance(debtor_id=1, creditor_id=2, amount=Decimal("0.00"))
    
    with pytest.raises(ValueError, match="must be positive"):
        Balance(debtor_id=1, creditor_id=2, amount=Decimal("-1.00"))


def test_balance_validation_rejects_same_debtor_creditor() -> None:
    """Test that Balance rejects same debtor and creditor."""
    with pytest.raises(ValueError, match="must be different"):
        Balance(debtor_id=1, creditor_id=1, amount=Decimal("10.00"))


def test_balance_validation_accepts_valid_balance() -> None:
    """Test that Balance accepts valid data."""
    balance = Balance(debtor_id=1, creditor_id=2, amount=Decimal("10.00"))
    assert balance.debtor_id == 1
    assert balance.creditor_id == 2
    assert balance.amount == Decimal("10.00")


def test_settlement_creation() -> None:
    """Test that Settlement can be created."""
    settlement = Settlement(
        id=None,
        settled_at=datetime.now(),
        note="All balances settled",
    )
    assert settlement.note == "All balances settled"


def test_model_replace_method() -> None:
    """Test that models have working replace method."""
    user = User(id=None, name="Alice", created_at=datetime.now())
    updated_user = user.replace(id=1, name="Alice Updated")
    
    assert user.id is None  # Original unchanged
    assert user.name == "Alice"
    assert updated_user.id == 1  # New instance updated
    assert updated_user.name == "Alice Updated"
