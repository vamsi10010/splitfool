"""
User Service Contract

Defines the interface for user management operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    """User entity."""
    id: int | None
    name: str
    created_at: datetime


class UserService(ABC):
    """
    Service for managing users.
    
    Responsibilities:
    - User CRUD operations (FR-001, FR-002, FR-003)
    - Name validation and uniqueness enforcement (FR-006, FR-007)
    - Balance check before deletion (FR-004)
    """
    
    @abstractmethod
    def create_user(self, name: str) -> User:
        """
        Create a new user.
        
        Args:
            name: User's name
            
        Returns:
            Created user with assigned ID
            
        Raises:
            ValidationError: If name is empty, whitespace-only, or exceeds 100 chars (USER_001, USER_002)
            DuplicateUserError: If name already exists (USER_003)
            
        Requirements: FR-001, FR-006, FR-007
        """
        pass
    
    @abstractmethod
    def get_user(self, user_id: int) -> User:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User entity
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        pass
    
    @abstractmethod
    def get_all_users(self) -> list[User]:
        """
        Retrieve all users.
        
        Returns:
            List of all users, ordered by name
            
        Requirements: Support user selection in UI
        """
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, new_name: str) -> User:
        """
        Update a user's name.
        
        Args:
            user_id: User's unique identifier
            new_name: New name for the user
            
        Returns:
            Updated user entity
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValidationError: If new name is invalid (USER_001, USER_002)
            DuplicateUserError: If new name already exists (USER_003)
            
        Requirements: FR-002, FR-006, FR-007
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        """
        Delete a user from the system.
        
        Args:
            user_id: User's unique identifier
            
        Raises:
            UserNotFoundError: If user doesn't exist
            UserHasBalancesError: If user has outstanding balances (USER_004)
            
        Requirements: FR-003, FR-004
        """
        pass
    
    @abstractmethod
    def user_has_balances(self, user_id: int) -> bool:
        """
        Check if a user has any outstanding balances.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user has balances (owes or is owed), False otherwise
            
        Requirements: FR-004 (validation for deletion)
        """
        pass
