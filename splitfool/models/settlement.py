"""Settlement entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Settlement:
    """Immutable settlement record representing bulk balance clearing.

    Attributes:
        id: Unique identifier (None for new settlements)
        settled_at: Timestamp when settlement occurred
        note: Optional user note about the settlement
    """

    id: int | None
    settled_at: datetime
    note: str

    def replace(self, **kwargs: object) -> "Settlement":
        """Create a new Settlement with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New Settlement instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
