"""Item entity model."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Item:
    """Immutable item entity representing a line item within a bill.

    Attributes:
        id: Unique identifier (None for new items)
        bill_id: ID of parent bill
        description: Description of the item
        cost: Cost of the item
    """

    id: int | None
    bill_id: int
    description: str
    cost: Decimal

    def __post_init__(self) -> None:
        """Validate item data.

        Raises:
            ValueError: If item data is invalid
        """
        if self.cost <= Decimal("0"):
            raise ValueError("Item cost must be positive")
        if len(self.description) > 200:
            raise ValueError("Description must be 200 characters or less")

    def replace(self, **kwargs: object) -> "Item":
        """Create a new Item with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New Item instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
