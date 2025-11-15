"""User service for business logic."""

import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

from splitfool.db.repositories.user_repository import UserRepository
from splitfool.models.user import User
from splitfool.services.validation import validate_user_name
from splitfool.utils.errors import UserHasBalancesError

if TYPE_CHECKING:
    from splitfool.services.balance_service import BalanceService


class UserService:
    """Service for user-related business logic."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize service with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection
        self.user_repo = UserRepository(connection)
        self._balance_service: "BalanceService | None" = None

    def set_balance_service(self, balance_service: "BalanceService") -> None:
        """Set balance service for checking user balances.

        Args:
            balance_service: Balance service instance
        """
        self._balance_service = balance_service

    def create_user(self, name: str) -> User:
        """Create a new user.

        Args:
            name: User's display name

        Returns:
            Created user

        Raises:
            ValidationError: If name is invalid
            DuplicateUserError: If name already exists
        """
        validate_user_name(name)
        
        user = User(
            id=None,
            name=name,
            created_at=datetime.now(),
        )
        
        return self.user_repo.create(user)

    def get_user(self, user_id: int) -> User:
        """Get user by ID.

        Args:
            user_id: ID of user to retrieve

        Returns:
            User instance

        Raises:
            UserNotFoundError: If user not found
        """
        return self.user_repo.get(user_id)

    def get_all_users(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users ordered by name
        """
        return self.user_repo.get_all()

    def update_user(self, user_id: int, name: str) -> User:
        """Update user's name.

        Args:
            user_id: ID of user to update
            name: New name for user

        Returns:
            Updated user

        Raises:
            ValidationError: If name is invalid
            UserNotFoundError: If user not found
            DuplicateUserError: If new name already exists
        """
        validate_user_name(name)
        
        # Get existing user
        user = self.user_repo.get(user_id)
        
        # Update with new name
        updated_user = user.replace(name=name)
        
        return self.user_repo.update(updated_user)

    def delete_user(self, user_id: int) -> None:
        """Delete user if they have no outstanding balances.

        Args:
            user_id: ID of user to delete

        Raises:
            UserNotFoundError: If user not found
            UserHasBalancesError: If user has outstanding balances
        """
        # Check if user has outstanding balances
        if self.user_has_balances(user_id):
            raise UserHasBalancesError(
                "Cannot delete user with outstanding balances",
                code="USER_005",
            )
        
        self.user_repo.delete(user_id)

    def user_has_balances(self, user_id: int) -> bool:
        """Check if user has outstanding balances.

        Args:
            user_id: ID of user to check

        Returns:
            True if user has balances, False otherwise
        """
        if self._balance_service is None:
            # If balance service not set, allow deletion (backward compatibility)
            return False
        
        return self._balance_service.user_has_outstanding_balances(user_id)
