"""Assignment entity model."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Assignment:
    """Immutable assignment entity linking items to users with fractions.

    Attributes:
        id: Unique identifier (None for new assignments)
        item_id: ID of the item being assigned
        user_id: ID of the user assigned to the item
        fraction: Portion of item cost (0.0 to 1.0)
    """

    id: int | None
    item_id: int
    user_id: int
    fraction: Decimal

    def __post_init__(self) -> None:
        """Validate assignment data.

        Raises:
            ValueError: If assignment data is invalid
        """
        if not (Decimal("0") < self.fraction <= Decimal("1")):
            raise ValueError("Fraction must be between 0 and 1")

    def replace(self, **kwargs: object) -> "Assignment":
        """Create a new Assignment with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New Assignment instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
