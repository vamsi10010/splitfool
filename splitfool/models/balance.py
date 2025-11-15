"""Balance entity model."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Balance:
    """Immutable balance entity representing debt between users.

    This is a derived entity - not stored in database but calculated from bills.

    Attributes:
        debtor_id: ID of user who owes money
        creditor_id: ID of user who is owed money
        amount: Net amount owed (always positive)
    """

    debtor_id: int
    creditor_id: int
    amount: Decimal

    def __post_init__(self) -> None:
        """Validate balance data.

        Raises:
            ValueError: If balance data is invalid
        """
        if self.amount <= Decimal("0"):
            raise ValueError("Balance amount must be positive")
        if self.debtor_id == self.creditor_id:
            raise ValueError("Debtor and creditor must be different users")

    def replace(self, **kwargs: object) -> "Balance":
        """Create a new Balance with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New Balance instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
