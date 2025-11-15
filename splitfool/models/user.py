"""User entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    """Immutable user entity representing a participant in bill splitting.

    Attributes:
        id: Unique identifier (None for new users)
        name: User's display name
        created_at: Timestamp when user was created
    """

    id: int | None
    name: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate user data on creation.

        Raises:
            ValueError: If user data is invalid
        """
        if not self.name or self.name.isspace():
            raise ValueError("User name cannot be empty")
        if len(self.name) > 100:
            raise ValueError("User name must be 100 characters or less")

    def replace(self, **kwargs: object) -> "User":
        """Create a new User with updated fields.

        Args:
            **kwargs: Fields to update

        Returns:
            New User instance with updated fields
        """
        from dataclasses import replace
        return replace(self, **kwargs)
