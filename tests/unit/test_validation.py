"""Unit tests for validation utilities."""

from decimal import Decimal

import pytest

from splitfool.models.assignment import Assignment
from splitfool.services.validation import (
    validate_bill_fractions,
    validate_positive_decimal,
    validate_user_name,
)
from splitfool.utils.errors import ValidationError


def test_validate_user_name_accepts_valid_name() -> None:
    """Test that validate_user_name accepts valid names."""
    validate_user_name("Alice")
    validate_user_name("Bob Smith")
    validate_user_name("A" * 100)  # Max length


def test_validate_user_name_rejects_empty() -> None:
    """Test that validate_user_name rejects empty names."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_user_name("")


def test_validate_user_name_rejects_whitespace() -> None:
    """Test that validate_user_name rejects whitespace-only names."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_user_name("   ")


def test_validate_user_name_rejects_too_long() -> None:
    """Test that validate_user_name rejects names over 100 characters."""
    with pytest.raises(ValidationError, match="100 characters or less"):
        validate_user_name("A" * 101)


def test_validate_bill_fractions_accepts_valid_fractions() -> None:
    """Test that validate_bill_fractions accepts fractions summing to 1.0."""
    assignments = [
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.5")),
        Assignment(id=None, item_id=1, user_id=2, fraction=Decimal("0.5")),
    ]
    validate_bill_fractions(assignments)


def test_validate_bill_fractions_accepts_single_user() -> None:
    """Test that validate_bill_fractions accepts single user with 1.0 fraction."""
    assignments = [
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("1.0")),
    ]
    validate_bill_fractions(assignments)


def test_validate_bill_fractions_accepts_unequal_split() -> None:
    """Test that validate_bill_fractions accepts unequal fractions summing to 1.0."""
    assignments = [
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.3")),
        Assignment(id=None, item_id=1, user_id=2, fraction=Decimal("0.7")),
    ]
    validate_bill_fractions(assignments)


def test_validate_bill_fractions_rejects_not_summing_to_one() -> None:
    """Test that validate_bill_fractions rejects fractions not summing to 1.0."""
    assignments = [
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.5")),
        Assignment(id=None, item_id=1, user_id=2, fraction=Decimal("0.4")),
    ]
    with pytest.raises(ValidationError, match="must equal 1.0"):
        validate_bill_fractions(assignments)


def test_validate_bill_fractions_handles_multiple_items() -> None:
    """Test that validate_bill_fractions validates each item separately."""
    assignments = [
        # Item 1: valid (0.5 + 0.5 = 1.0)
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("0.5")),
        Assignment(id=None, item_id=1, user_id=2, fraction=Decimal("0.5")),
        # Item 2: valid (1.0)
        Assignment(id=None, item_id=2, user_id=1, fraction=Decimal("1.0")),
    ]
    validate_bill_fractions(assignments)


def test_validate_bill_fractions_detects_invalid_item_in_multiple() -> None:
    """Test that validate_bill_fractions detects invalid item among valid ones."""
    assignments = [
        # Item 1: valid
        Assignment(id=None, item_id=1, user_id=1, fraction=Decimal("1.0")),
        # Item 2: invalid (0.5 + 0.4 = 0.9)
        Assignment(id=None, item_id=2, user_id=1, fraction=Decimal("0.5")),
        Assignment(id=None, item_id=2, user_id=2, fraction=Decimal("0.4")),
    ]
    with pytest.raises(ValidationError, match="Item 2.*must equal 1.0"):
        validate_bill_fractions(assignments)


def test_validate_positive_decimal_accepts_positive() -> None:
    """Test that validate_positive_decimal accepts positive values."""
    validate_positive_decimal(Decimal("0.01"))
    validate_positive_decimal(Decimal("100.00"))


def test_validate_positive_decimal_rejects_zero() -> None:
    """Test that validate_positive_decimal rejects zero."""
    with pytest.raises(ValidationError, match="must be positive"):
        validate_positive_decimal(Decimal("0"))


def test_validate_positive_decimal_rejects_negative() -> None:
    """Test that validate_positive_decimal rejects negative values."""
    with pytest.raises(ValidationError, match="must be positive"):
        validate_positive_decimal(Decimal("-1.00"))
