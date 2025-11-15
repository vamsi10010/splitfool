"""Input validation utilities for business logic."""

from decimal import Decimal
from typing import TYPE_CHECKING

from splitfool.utils.errors import ValidationError

if TYPE_CHECKING:
    from splitfool.models.assignment import Assignment


def validate_user_name(name: str) -> None:
    """Validate user name is not empty and within length limits.

    Args:
        name: User name to validate

    Raises:
        ValidationError: If name is invalid
    """
    if not name or name.isspace():
        raise ValidationError("User name cannot be empty.", code="USER_001")
    if len(name) > 100:
        raise ValidationError(
            "User name must be 100 characters or less.", code="USER_002"
        )


def validate_bill_fractions(assignments: list["Assignment"]) -> None:
    """Validate fractions sum to 1.0 for each item.

    Args:
        assignments: List of assignments to validate

    Raises:
        ValidationError: If fractions don't sum to 1.0 for any item
    """
    item_fractions: dict[int, Decimal] = {}
    
    for assignment in assignments:
        item_id = assignment.item_id
        item_fractions[item_id] = (
            item_fractions.get(item_id, Decimal("0")) + assignment.fraction
        )
    
    for item_id, total in item_fractions.items():
        if abs(total - Decimal("1.0")) > Decimal("0.001"):
            raise ValidationError(
                f"Item {item_id} fractions sum to {total}, must equal 1.0",
                code="ASSIGN_002",
            )


def validate_positive_decimal(value: Decimal, field_name: str = "value") -> None:
    """Validate that a decimal value is positive.

    Args:
        value: Decimal value to validate
        field_name: Name of field for error message

    Raises:
        ValidationError: If value is not positive
    """
    if value <= Decimal("0"):
        raise ValidationError(
            f"{field_name} must be positive, got {value}", code="VALIDATION_001"
        )
