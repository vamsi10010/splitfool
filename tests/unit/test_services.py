"""Unit tests for service layer."""

from datetime import datetime

import pytest

from splitfool.models.user import User
from splitfool.services.user_service import UserService
from splitfool.utils.errors import (
    DuplicateUserError,
    UserHasBalancesError,
    UserNotFoundError,
    ValidationError,
)
from tests.fixtures import in_memory_db


def test_user_service_create_user(in_memory_db):  # type: ignore
    """Test creating a user through service."""
    service = UserService(in_memory_db)
    
    user = service.create_user("Alice")
    
    assert user.id is not None
    assert user.name == "Alice"


def test_user_service_create_user_validates_name(in_memory_db):  # type: ignore
    """Test that create_user validates user name."""
    service = UserService(in_memory_db)
    
    with pytest.raises(ValidationError, match="cannot be empty"):
        service.create_user("")
    
    with pytest.raises(ValidationError, match="cannot be empty"):
        service.create_user("   ")
    
    with pytest.raises(ValidationError, match="100 characters or less"):
        service.create_user("A" * 101)


def test_user_service_create_user_rejects_duplicate(in_memory_db):  # type: ignore
    """Test that create_user rejects duplicate names."""
    service = UserService(in_memory_db)
    
    service.create_user("Alice")
    
    with pytest.raises(DuplicateUserError):
        service.create_user("Alice")


def test_user_service_get_user(in_memory_db):  # type: ignore
    """Test getting a user by ID."""
    service = UserService(in_memory_db)
    created_user = service.create_user("Alice")
    
    retrieved_user = service.get_user(created_user.id)  # type: ignore
    
    assert retrieved_user.id == created_user.id
    assert retrieved_user.name == "Alice"


def test_user_service_get_user_not_found(in_memory_db):  # type: ignore
    """Test that get_user raises error for non-existent user."""
    service = UserService(in_memory_db)
    
    with pytest.raises(UserNotFoundError):
        service.get_user(999)


def test_user_service_get_all_users(in_memory_db):  # type: ignore
    """Test getting all users."""
    service = UserService(in_memory_db)
    service.create_user("Alice")
    service.create_user("Bob")
    service.create_user("Charlie")
    
    all_users = service.get_all_users()
    
    assert len(all_users) == 3
    assert all_users[0].name == "Alice"  # Sorted by name
    assert all_users[1].name == "Bob"
    assert all_users[2].name == "Charlie"


def test_user_service_update_user(in_memory_db):  # type: ignore
    """Test updating a user's name."""
    service = UserService(in_memory_db)
    user = service.create_user("Alice")
    
    updated_user = service.update_user(user.id, "Alice Smith")  # type: ignore
    
    assert updated_user.name == "Alice Smith"
    assert updated_user.id == user.id


def test_user_service_update_user_validates_name(in_memory_db):  # type: ignore
    """Test that update_user validates new name."""
    service = UserService(in_memory_db)
    user = service.create_user("Alice")
    
    with pytest.raises(ValidationError, match="cannot be empty"):
        service.update_user(user.id, "")  # type: ignore
    
    with pytest.raises(ValidationError, match="100 characters or less"):
        service.update_user(user.id, "A" * 101)  # type: ignore


def test_user_service_update_user_rejects_duplicate_name(in_memory_db):  # type: ignore
    """Test that update_user rejects duplicate names."""
    service = UserService(in_memory_db)
    user1 = service.create_user("Alice")
    user2 = service.create_user("Bob")
    
    with pytest.raises(DuplicateUserError):
        service.update_user(user2.id, "Alice")  # type: ignore


def test_user_service_update_user_not_found(in_memory_db):  # type: ignore
    """Test that update_user raises error for non-existent user."""
    service = UserService(in_memory_db)
    
    with pytest.raises(UserNotFoundError):
        service.update_user(999, "New Name")


def test_user_service_delete_user(in_memory_db):  # type: ignore
    """Test deleting a user."""
    service = UserService(in_memory_db)
    user = service.create_user("Alice")
    
    service.delete_user(user.id)  # type: ignore
    
    with pytest.raises(UserNotFoundError):
        service.get_user(user.id)  # type: ignore


def test_user_service_delete_user_not_found(in_memory_db):  # type: ignore
    """Test that delete_user raises error for non-existent user."""
    service = UserService(in_memory_db)
    
    with pytest.raises(UserNotFoundError):
        service.delete_user(999)


def test_user_service_user_has_balances_stub(in_memory_db):  # type: ignore
    """Test that user_has_balances is stubbed to return False."""
    service = UserService(in_memory_db)
    user = service.create_user("Alice")
    
    # Stub implementation always returns False for Phase 3
    assert service.user_has_balances(user.id) is False  # type: ignore


def test_user_service_delete_with_balances_check(in_memory_db):  # type: ignore
    """Test that delete checks for balances (stub in Phase 3)."""
    service = UserService(in_memory_db)
    user = service.create_user("Alice")
    
    # Since stub returns False, deletion should succeed
    service.delete_user(user.id)  # type: ignore
    
    with pytest.raises(UserNotFoundError):
        service.get_user(user.id)  # type: ignore
