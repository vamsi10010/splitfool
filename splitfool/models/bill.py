"""Bill entity model."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Bill:
    """Immutable bill entity representing a single expense event.

    Attributes:
        id: Unique identifier (None for new bills)
        payer_id: ID of user who paid the bill
        description: Description of the bill
        tax: Additional costs (tax, tip, fees)
        created_at: Timestamp when bill was created
    """

    id: int | None
    payer_id: int
    description: str
    tax: Decimal
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate bill data.

        Raises:
            ValueError: If bill data is invalid
        """
        if self.tax < Decimal("0"):
            raise ValueError("Tax must be non-negative")
        if len(self.description) > 500:
            raise ValueError("Description must be 500 characters or less")

    def replace(self, **kwargs: object) -> "Bill":
        """Create a new Bill with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New Bill instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
